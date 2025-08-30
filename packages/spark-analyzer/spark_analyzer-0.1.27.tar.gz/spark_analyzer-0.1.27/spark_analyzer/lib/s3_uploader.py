import requests
import logging
import configparser
import os
import json
import time
import random
from typing import List, Dict, Any, Optional

# Modern replacement for pkg_resources
try:
    from importlib.resources import files
    MODERN_RESOURCES = True
except ImportError:
    # Fallback for older Python versions
    import pkg_resources
    MODERN_RESOURCES = False

class S3Uploader:
    DEFAULT_API_BASE_URL = "https://api.onehouse.ai"
    DEFAULT_API_KEY = "GUlrctAWTaYb5h2JSSaWOA=="
    DEFAULT_API_SECRET = "WuktR7CcKLTSk+barqq+QemYVefflR0cImQo5+9qhEg="
    DEFAULT_ORG_ID = "aa6e0325-1987-4295-a140-02bf22adce1e"
    DEFAULT_USER_ID = "As1xjFqiiDUKdtrCnMk8Yp4PhzQ2"
    
    MAX_RETRIES = 3
    RETRY_DELAY_MS = 1000
    MAX_RETRY_DELAY_MS = 10000
    
    ACCEPTABLE_FAILURE_STATUS_CODES = [400, 401, 403, 404, 409]
    
    def __init__(self, config_file: str = "config.ini", use_staging: bool = False, args=None):
        """Initialize the S3Uploader with configuration values."""
        self.use_staging = use_staging
        self.staging_explicitly_requested = use_staging
        self.config = configparser.ConfigParser()
        self.args = args
        
        config_paths = [
        ]
        
        if MODERN_RESOURCES:
            try:
                resource_path = files("spark_analyzer").joinpath("lib", "configs", config_file)
                config_paths.append(str(resource_path))
            except Exception:
                pass  
        else:
            try:
                config_paths.append(pkg_resources.resource_filename("spark_analyzer", os.path.join("lib", "configs", config_file)))
            except Exception:
                pass  
        
        # Add local paths
        config_paths.extend([
            os.path.join("lib", "configs", config_file),
            os.path.join(os.path.expanduser("~"), ".spark_analyzer", "configs", config_file)
        ])
        
        config_found = False
        self.config_path_used = None
        
        for path in config_paths:
            if os.path.exists(path):
                try:
                    self.config.read(path)
                    config_found = True
                    self.config_path_used = os.path.abspath(path)
                    logging.debug(f"Using configuration from: {self.config_path_used}")
                    break
                except configparser.ParsingError as e:
                    logging.error(f"Error parsing config file {path}: {str(e)}")
                    continue
        
        if not config_found:
            logging.warning("Configuration file not found. Using default values.")
            self.config_path_used = None
        
        if self.use_staging:
            self._setup_staging_environment()
        else:
            self._setup_production_environment()
    
    def _setup_staging_environment(self):
        """Set up the staging environment configuration."""
        self.api_base_url = os.environ.get('SPARK_ANALYZER_STAGING_API_URL', '')
        self.api_key = os.environ.get('SPARK_ANALYZER_STAGING_API_KEY', '')
        self.api_secret = os.environ.get('SPARK_ANALYZER_STAGING_API_SECRET', '')
        self.org_id = os.environ.get('SPARK_ANALYZER_STAGING_ORG_ID', '')
        self.user_id = os.environ.get('SPARK_ANALYZER_STAGING_USER_ID', '')
        self.cost_estimator_user_id = os.environ.get('SPARK_ANALYZER_STAGING_COST_ESTIMATOR_USER_ID', '')
        
        missing_env_vars = []
        for name, value in [
            ('SPARK_ANALYZER_STAGING_API_URL', self.api_base_url),
            ('SPARK_ANALYZER_STAGING_API_KEY', self.api_key),
            ('SPARK_ANALYZER_STAGING_API_SECRET', self.api_secret),
            ('SPARK_ANALYZER_STAGING_ORG_ID', self.org_id),
            ('SPARK_ANALYZER_STAGING_USER_ID', self.user_id)
        ]:
            if not value:
                missing_env_vars.append(name)
        
        if missing_env_vars:
            logging.error(f"Staging environment requested but cannot be used: Missing {', '.join(missing_env_vars)}")
            self.upload_enabled = False
            return
        
        if not self.cost_estimator_user_id:
            logging.error("Staging mode active but SPARK_ANALYZER_STAGING_COST_ESTIMATOR_USER_ID not set")
            self.upload_enabled = False
            return
        
        self.upload_enabled = True
        logging.info("Using staging environment")
    
    def _setup_production_environment(self):
        """Set up the production environment configuration."""
        logging.info("Using production environment")
        self.api_base_url = self.config.get('production', 'api_base_url', fallback=self.DEFAULT_API_BASE_URL)
        self.api_key = self.config.get('production', 'api_key', fallback=self.DEFAULT_API_KEY)
        self.api_secret = self.config.get('production', 'api_secret', fallback=self.DEFAULT_API_SECRET)
        self.org_id = self.config.get('production', 'org_id', fallback=self.DEFAULT_ORG_ID)
        self.user_id = self.config.get('production', 'user_id', fallback=self.DEFAULT_USER_ID)
        self.cost_estimator_user_id = None
        
        if self.args and hasattr(self.args, 'cost_estimator_id') and self.args.cost_estimator_id:
            self.cost_estimator_user_id = self.args.cost_estimator_id
            logging.info(f"Using cost estimator user ID from command line: {self.cost_estimator_user_id}")
        else:
            config_user_id = self.config.get('cost_estimator', 'user_id', fallback='')
            if config_user_id:
                self.cost_estimator_user_id = config_user_id
                logging.info(f"Using cost estimator user ID: {self.cost_estimator_user_id}")
        
        self.upload_enabled = bool(self.user_id) and bool(self.cost_estimator_user_id)
        
        if not self.upload_enabled:
            if not self.cost_estimator_user_id:
                logging.error("S3 upload disabled: cost estimator user ID not configured")
            elif not self.user_id:
                logging.error("S3 upload disabled: project user ID not configured")
        else:
            env_name = "production"
            logging.info(f"Using {env_name} environment for API endpoints")
            logging.debug(f"API base URL: {self.api_base_url}")
            logging.debug(f"Organization ID: {self.org_id}")
            if self.cost_estimator_user_id:
                logging.info(f"Using cost estimator user ID: {self.cost_estimator_user_id}")
    
    def is_staging_mode(self) -> bool:
        """Return whether we're using staging mode."""
        return self.use_staging
        
    def was_staging_explicitly_requested(self) -> bool:
        """Return whether staging mode was explicitly requested."""
        return self.staging_explicitly_requested
    
    def _calculate_retry_delay(self, retry_count: int) -> float:
        """Calculate retry delay with exponential backoff and jitter."""
        delay_ms = min(
            self.RETRY_DELAY_MS * (2 ** retry_count),
            self.MAX_RETRY_DELAY_MS
        )
        jitter_ms = random.uniform(-delay_ms/2, delay_ms/2)
        final_delay_ms = delay_ms + jitter_ms
        return max(0.001, final_delay_ms / 1000)
    
    def _make_api_request(self, endpoint: str, data: Dict[str, Any], method: str = 'post') -> Optional[Dict[str, Any]]:
        if not self.upload_enabled:
            logging.warning("S3 upload is not enabled. Please check your configuration.")
            return None
            
        url = f"{self.api_base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "x-onehouse-api-key": self.api_key,
            "x-onehouse-api-secret": self.api_secret,
            "x-onehouse-uuid": self.user_id,
            "x-onehouse-project-uid": self.org_id
        }
        
        if self.cost_estimator_user_id:
            headers["x-cost-estimator-user-id"] = self.cost_estimator_user_id
        
        logging.debug(f"Making {method.upper()} request to: {url}")
        logging.debug(f"Request payload: {json.dumps(data)}")
        
        for retry_count in range(self.MAX_RETRIES):
            try:
                logging.info(f"Making {method.upper()} request to API (attempt {retry_count + 1}/{self.MAX_RETRIES})")
                
                if method == 'post':
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                elif method == 'put':
                    response = requests.put(url, headers=headers, json=data, timeout=30)
                else:
                    logging.error(f"Unsupported HTTP method: {method}")
                    return None
                
                status_code = response.status_code
                response_text = response.text[:1000] if response.text else "(empty)"
                
                logging.debug(f"Response status code: {status_code}")
                logging.debug(f"Response content: {response_text}")
                
                if status_code in [200, 204]:
                    logging.info(f"API request successful: {status_code}")
                    try:
                        if response.text and response.text.strip():
                            response_data = response.json()
                            logging.debug(f"Response data: {json.dumps(response_data)[:200]}...")
                            logging.debug(f"Response keys: {list(response_data.keys())}")
                            return response_data
                        else:
                            logging.debug("Response has no content (empty response)")
                            return {"status": "success"}
                    except json.JSONDecodeError:
                        logging.debug("Response is not valid JSON, but status code indicates success")
                        return {"status": "success"}
                    except Exception as e:
                        logging.debug(f"Error parsing response content: {str(e)}")
                        return {"status": "success"}
                
                if status_code in self.ACCEPTABLE_FAILURE_STATUS_CODES:
                    error_message = f"API request failed with status code: {status_code}"
                    try:
                        logging.debug(f"{error_message} - {response_text}")
                        logging.debug(f"Request URL: {url}")
                        logging.debug(f"Request data: {json.dumps(data)}")
                        
                        if self.args and hasattr(self.args, 'debug') and self.args.debug:
                            logging.error(error_message)
                        
                        if status_code == 400:
                            logging.error("Bad request - The server could not understand the request")
                            if "invalid" in response_text.lower():
                                logging.error("This may be due to invalid parameters or payload format")
                            
                            try:
                                error_json = json.loads(response_text)
                                if 'message' in error_json:
                                    logging.debug(f"Server error message: {error_json['message']}")
                                elif 'error' in error_json:
                                    logging.debug(f"Server error message: {error_json['error']}")
                                elif 'description' in error_json:
                                    logging.debug(f"Server error message: {error_json['description']}")
                            except:
                                logging.debug(f"Raw error response: {response_text[:300]}")
                                
                        elif status_code == 401:
                            logging.error("Unauthorized - Authentication credentials are invalid")
                            logging.error("Check your API key and secret")
                        elif status_code == 403:
                            logging.error("Forbidden - You don't have permission for this operation")
                            logging.error("Verify your organization ID and user ID are correct")
                        elif status_code == 404:
                            if self.args and hasattr(self.args, 'debug') and self.args.debug:
                                logging.error("Not found - The requested resource does not exist")
                                logging.error("Check that the endpoint is correct")
                    except:
                        logging.error(error_message)
                    
                    return None
                
                if retry_count < self.MAX_RETRIES - 1:
                    delay = self._calculate_retry_delay(retry_count)
                    logging.warning(
                        f"API request failed: {status_code}. "
                        f"Retrying in {delay:.2f} seconds (attempt {retry_count + 1}/{self.MAX_RETRIES})"
                    )
                    try:
                        logging.debug(f"Response body: {response.text[:500]}")
                    except:
                        pass
                    
                    time.sleep(delay)
                else:
                    logging.error(f"API request failed after {self.MAX_RETRIES} attempts: {status_code}")
                    try:
                        logging.error(f"Final error response: {response.text[:500]}")
                    except:
                        pass
                    return None
                    
            except requests.exceptions.ConnectionError as e:
                if retry_count < self.MAX_RETRIES - 1:
                    delay = self._calculate_retry_delay(retry_count)
                    logging.warning(
                        f"Connection error: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds (attempt {retry_count + 1}/{self.MAX_RETRIES})"
                    )
                    time.sleep(delay)
                else:
                    logging.error(f"Connection error after {self.MAX_RETRIES} attempts: {str(e)}")
                    logging.error("Could not connect to the API server. Check your internet connection.")
                    return None
            except requests.exceptions.Timeout as e:
                if retry_count < self.MAX_RETRIES - 1:
                    delay = self._calculate_retry_delay(retry_count)
                    logging.warning(
                        f"Request timed out: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds (attempt {retry_count + 1}/{self.MAX_RETRIES})"
                    )
                    time.sleep(delay)
                else:
                    logging.error(f"Request timed out after {self.MAX_RETRIES} attempts: {str(e)}")
                    logging.error("The API server is not responding. Try again later.")
                    return None
            except Exception as e:
                if retry_count < self.MAX_RETRIES - 1:
                    delay = self._calculate_retry_delay(retry_count)
                    logging.warning(
                        f"Error making API request: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds (attempt {retry_count + 1}/{self.MAX_RETRIES})"
                    )
                    time.sleep(delay)
                else:
                    logging.error(f"Error making API request after {self.MAX_RETRIES} attempts: {str(e)}")
                    logging.error(f"Exception type: {type(e).__name__}")
                    return None
        
        return None
    
    def get_presigned_urls(self, application_id: str, file_list: List[str]) -> Optional[List[str]]:
        """Get pre-signed URLs for uploading stage metadata files to S3."""
        user_id_for_endpoint = self.cost_estimator_user_id if self.cost_estimator_user_id else self.user_id
        endpoint = f"/v1/costEstimator/{user_id_for_endpoint}/{application_id}/upload-urls"
        payload = {
            "cost_estimator_user_id": user_id_for_endpoint,
            "application_id": application_id,
            "stage_metadata_files": file_list
        }
        logging.info(f"Requesting pre-signed URLs for application {application_id} with {len(file_list)} files")
        response = self._make_api_request(endpoint, payload)

        if not response:
            if self.args and hasattr(self.args, 'debug') and self.args.debug:
                logging.error(f"Failed to get pre-signed URLs for application {application_id}")
            return None

        urls = []
        if "presigned_urls" in response:
            urls = response["presigned_urls"]
        elif "presignedUrls" in response:
            urls = response["presignedUrls"]
        else:
            for key in response.keys():
                if isinstance(response[key], list) and len(response[key]) > 0:
                    if key.lower().endswith('urls') or 'url' in key.lower():
                        urls = response[key]
                        break

        logging.info(f"Received {len(urls)} pre-signed URLs")
        if len(urls) != len(file_list):
            logging.warning(f"Requested {len(file_list)} URLs but received {len(urls)} URLs")
        invalid_urls = [url for url in urls if not url.startswith("http")]
        if invalid_urls:
            logging.warning(f"Received {len(invalid_urls)} invalid-looking URLs")
        return urls
    
    def upload_file(self, presigned_url: str, file_path: str, content_type: str = "application/json") -> bool:
        """Upload a file to S3 using a pre-signed URL."""
        try:
            logging.info(f"Uploading file {file_path} to S3")
            
            if not os.path.exists(file_path):
                logging.error(f"File not found: {file_path}")
                return False
                
            file_size = os.path.getsize(file_path)
            logging.debug(f"File size: {file_size} bytes")
            
            with open(file_path, 'rb') as f:
                headers = {"Content-Type": content_type}
                response = requests.put(presigned_url, data=f, headers=headers)
                
                if response.status_code in [200, 204]:
                    logging.info(f"Successfully uploaded {file_path} to S3")
                    return True
                else:
                    logging.error(f"Upload failed with status code: {response.status_code}")
                    return False
                    
        except Exception as e:
            logging.error(f"Error uploading file {file_path}: {str(e)}")
            return False
    
    def signal_application_completion(self, application_id: str, file_list: List[str]) -> bool:
        """Signal that all files for an application have been uploaded."""
        user_id_for_endpoint = self.cost_estimator_user_id if self.cost_estimator_user_id else self.user_id
        endpoint = f"/v1/costEstimator/{user_id_for_endpoint}/{application_id}/publish"
        payload = {
            "cost_estimator_user_id": user_id_for_endpoint,
            "application_id": application_id,
            "stage_metadata_files": file_list
        }
        logging.info(f"Signaling completion for application {application_id} with {len(file_list)} files")
        logging.debug(f"API endpoint: /v1/costEstimator/{user_id_for_endpoint}/{application_id}/publish (marks individual application as uploaded)")
        logging.debug(f"Payload: {json.dumps(payload)}")
        response = self._make_api_request(endpoint, payload)
        if response is not None:
            logging.info(f"Successfully signaled completion for application {application_id}")
            return True
        else:
            logging.error(f"Failed to signal completion for application {application_id}")
            return False
    
    def signal_all_jobs_completion(self, application_ids: List[str]) -> bool:
        """Signal that all applications have been processed."""
        user_id_for_endpoint = self.cost_estimator_user_id if self.cost_estimator_user_id else self.user_id
        endpoint = f"/v1/costEstimator/{user_id_for_endpoint}/publish"
        payload = {
            "cost_estimator_user_id": user_id_for_endpoint,
            "spark_applications": application_ids
        }
        logging.info(f"Signaling completion for all {len(application_ids)} applications")
        response = self._make_api_request(endpoint, payload)
        if response is not None:
            logging.info(f"Successfully signaled completion for all applications")
            return True
        else:
            logging.error(f"Failed to signal completion for all applications")
            return False
    
    def is_upload_enabled(self) -> bool:
        return self.upload_enabled
    
    def get_config_file_path(self) -> Optional[str]:
        """Return the path to the config file that was used."""
        return self.config_path_used
    
    def upload_json_data(self, presigned_url: str, json_data: str, content_type: str = "application/json") -> bool:
        """Upload a JSON string directly to S3 using a pre-signed URL."""
        try:
            logging.info("Uploading JSON data to S3")
            headers = {"Content-Type": content_type}
            response = requests.put(presigned_url, data=json_data.encode("utf-8"), headers=headers)
            if response.status_code in [200, 204]:
                logging.info("Successfully uploaded JSON data to S3")
                return True
            logging.error(f"Upload failed with status code: {response.status_code}")
            return False
        except Exception as e:
            logging.error(f"Error uploading JSON data: {str(e)}")
            return False 