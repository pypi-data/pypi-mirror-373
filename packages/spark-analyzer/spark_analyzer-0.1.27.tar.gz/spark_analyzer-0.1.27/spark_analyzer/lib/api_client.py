import requests
from typing import Dict, Any, Optional, Union, Callable, Tuple
import json
import configparser
import os
import argparse
import logging
import sys
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from ..utils.formatting import print_error_box

# Modern replacement for pkg_resources
try:
    from importlib.resources import files
    MODERN_RESOURCES = True
except ImportError:
    # Fallback for older Python versions
    import pkg_resources
    MODERN_RESOURCES = False

class APIClient:
    """Client for interacting with the server API."""
    
    def __init__(self, base_url="http://localhost:18080", args=None):
        """
        Initialize the API client.
        
        Args:
            base_url: Default base URL for the Spark History Server
            args: Command line arguments
        """
        self.config = configparser.ConfigParser()
        config_file = "config.ini"
        config_found = False
        
        config_paths = [
            os.path.expanduser(f"~/.spark_analyzer/{config_file}")
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                if not os.access(path, os.R_OK):
                    logging.warning(f"Config file exists but is not readable: {path}")
                    print(f"⚠️  Warning: Config file {path} exists but cannot be read.")
                    print(f"   Please check file permissions (try: chmod +r {path})")
                    continue
                
                try:
                    self.config.read(path)
                    config_found = True
                    self.config_path_used = os.path.abspath(path)
                    logging.debug(f"Using configuration from: {self.config_path_used}")
                    
                    if 'server' in self.config and 'base_url' in self.config['server']:
                        logging.debug(f"Config contains server.base_url = {self.config['server']['base_url']}")
                        relative_path = os.path.relpath(self.config_path_used, os.getcwd())
                        print(f"ℹ️  Using config file: {relative_path}")
                    else:
                        if 'connection' in self.config and self.config.get('connection', 'mode') == 'browser':
                            logging.debug(f"Browser mode detected - server.base_url not required")
                        else:
                            logging.debug(f"Config does not contain server.base_url")
                            print(f"⚠️  Config file found but missing server.base_url parameter: {self.config_path_used}")
                    
                    break
                except configparser.ParsingError as e:
                    logging.error(f"Error parsing config file {path}: {str(e)}")
                    print(f"⚠️  Warning: Configuration file {path} has syntax errors and could not be loaded.")
                    print(f"   Please check the file format and try again.")
                    continue
                
        if not config_found:
            logging.debug("Configuration file not found - will use default base_url")
        
        # Priority: 1. Command line arg 2. Environment variable 3. Config file 4. Default URL
        if args and hasattr(args, 'server_url') and args.server_url:
            self.base_url = args.server_url
            logging.debug(f"Using server URL from command line: {self.base_url}")
        elif args and hasattr(args, 'env') and args.env == 'staging':
            env_var_url = os.environ.get('SPARK_ANALYZER_STAGING_HISTORY_SERVER_URL')
            if env_var_url:
                self.base_url = env_var_url
                logging.debug(f"Using server URL from environment: {self.base_url}")
            else:
                self.base_url = base_url
                logging.debug(f"Using default server URL: {self.base_url}")
        elif 'server' in self.config and 'base_url' in self.config['server']:
            self.base_url = self.config['server']['base_url']
            logging.debug(f"Using server URL from config: {self.base_url}")
        else:
            self.base_url = base_url
            logging.debug(f"Using default server URL: {self.base_url}")
        
        self.original_url = self.base_url
        self.args = args
        self._app_attempt_cache = {}
        
        logging.info(f"Using Spark History Server URL: {self.base_url}")
        
        if self.base_url.count('/') > 3 and not '/api/v1' in self.base_url:
            logging.info(f"Detected custom path in URL. API endpoints will be appended as {self.base_url}/api/v1/...")
        
        self.live_app = False
        if 'processing' in self.config and 'live_app' in self.config['processing']:
            try:
                self.live_app = self.config.getboolean('processing', 'live_app')
                logging.debug(f"Live app setting from config: {self.live_app}")
            except (ValueError, configparser.Error):
                logging.warning("Invalid live_app setting in config, using default: False")
                self.live_app = False
        
        self._init_session()
        self._init_cookies()
        self._init_workflow_keywords()
        
    def _init_session(self):
        """Initialize the HTTP session with retry strategy."""
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.timeout = 60
        self.headers = self.get_headers()
    
    def _init_cookies(self):
        """Initialize cookies for browser mode authentication."""
        self.raw_cookies = None
        if self.args and self.args.browser:
            env_suffix = ""
            if hasattr(self.args, 'env') and self.args.env:
                env_suffix = f"_{self.args.env}"
            
            is_databricks = ("databricks.com" in self.base_url and "sparkui" in self.base_url) or ("azuredatabricks.net" in self.base_url and "sparkui" in self.base_url)
            
            if is_databricks:
                cookie_paths = [
                    os.path.expanduser(f"~/.spark_analyzer/databricks_cookies{env_suffix}.txt"),
                    os.path.expanduser("~/.spark_analyzer/databricks_cookies.txt")
                ]
                cookie_type = "Databricks"
            else:
                cookie_paths = [
                    os.path.expanduser(f"~/.spark_analyzer/raw_cookies{env_suffix}.txt"),
                    os.path.expanduser("~/.spark_analyzer/raw_cookies.txt")
                ]
                cookie_type = "browser"
            
            self._load_cookies_from_files(cookie_paths, cookie_type)
    
    def _load_cookies_from_files(self, cookie_paths, cookie_type):
        """Load cookies from the specified file paths."""
        cookie_found = False
        file_exists_but_empty = False
        
        for path in cookie_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        raw_content = f.read().strip()
                        
                        non_comment_lines = [line for line in raw_content.split('\n') if line.strip() and not line.strip().startswith('#')]
                        
                        if non_comment_lines:
                            self.raw_cookies = '\n'.join(non_comment_lines)
                            cookie_found = True
                            logging.debug(f"Using {cookie_type} cookies from: {path}")
                            break
                        else:
                            file_exists_but_empty = True
                except Exception as e:
                    logging.error(f"Error reading {cookie_type} cookie file {path}: {str(e)}")
                    continue
                
        if not cookie_found:
            self._handle_missing_cookies(cookie_paths, cookie_type, file_exists_but_empty)
        else:
            self._parse_cookies(cookie_type)
    
    def _handle_missing_cookies(self, cookie_paths, cookie_type, file_exists_but_empty):
        """Handle cases where cookies are missing or files are empty."""
        # Don't show warnings for browser mode since cookies will be collected at runtime
        if hasattr(self.args, 'browser') and self.args.browser:
            logging.debug(f"Browser mode detected - cookies will be collected at runtime")
            return
        
        if file_exists_but_empty:
            print(f"⚠️  {cookie_type.capitalize()} cookie file found but contains no actual cookies: {cookie_type.capitalize()} mode authentication may fail.")
            print("   Edit the file with your browser cookies:")
            found_path = next((p for p in cookie_paths if os.path.exists(p)), None)
            if found_path:
                print(f"   {os.path.abspath(found_path)}")
        else:
            print(f"⚠️  {cookie_type.capitalize()} cookie file not found: {cookie_type.capitalize()} mode authentication may fail.")
            print("   To use browser mode, create the cookie file at:")
            if "databricks" in cookie_type.lower():
                print("   ~/.spark_analyzer/databricks_cookies.txt")
            else:
                print("   ~/.spark_analyzer/raw_cookies.txt")
            print("   Then edit the file with your browser cookies")
    
    def _parse_cookies(self, cookie_type):
        """Parse the raw cookies into a dictionary."""
        try:
            self.cookie_dict = {}
            if "; " in self.raw_cookies:
                for item in self.raw_cookies.split("; "):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        self.cookie_dict[key.strip()] = value.strip()
            elif ";" in self.raw_cookies:
                for item in self.raw_cookies.split(";"):
                    item = item.strip()
                    if "=" in item:
                        key, value = item.split("=", 1)
                        self.cookie_dict[key.strip()] = value.strip()
            elif "=" in self.raw_cookies:
                key, value = self.raw_cookies.split("=", 1)
                self.cookie_dict[key.strip()] = value.strip()
            
            if not self.cookie_dict:
                logging.warning(f"Failed to parse {cookie_type} cookies. Cookie format may be invalid.")
            else:
                logging.info(f"Successfully parsed {len(self.cookie_dict)} {cookie_type} cookies")
        except Exception as e:
            logging.error(f"Error parsing {cookie_type} cookies: {str(e)}")
    
    def set_cookies_from_string(self, cookie_string):
        """Set cookies directly from a string instead of reading from files."""
        if not cookie_string or not cookie_string.strip():
            logging.warning("Empty cookie string provided")
            return False
        
        self.raw_cookies = cookie_string.strip()
        self._parse_cookies("runtime")
        
        # Set cookies in the session
        if self.cookie_dict:
            for key, value in self.cookie_dict.items():
                self.session.cookies.set(key, value)
            logging.info(f"Successfully set {len(self.cookie_dict)} cookies in session")
            return True
        else:
            logging.warning("Failed to parse cookies from string")
            return False
    
    def _init_workflow_keywords(self):
        """Initialize workflow type keywords for stage classification."""
        self.workflow_type_keywords = {}
        try:
            # Try to load workflow type keywords using the same path resolution as SparkStageAnalyzer
            keyword_paths = []
            
            # Get the directory of the current file (api_client.py)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct path to the resources directory
            resources_dir = os.path.join(os.path.dirname(current_dir), 'resources')
            keywords_file = os.path.join(resources_dir, 'workflow_type_keywords.json')
            keyword_paths.append(keywords_file)
            
            # Add package resource path using modern or legacy approach
            if MODERN_RESOURCES:
                try:
                    resource_path = files("spark_analyzer").joinpath("resources", "workflow_type_keywords.json")
                    keyword_paths.append(str(resource_path))
                except Exception:
                    pass  # Fallback to local path only
            else:
                try:
                    keyword_paths.append(pkg_resources.resource_filename("spark_analyzer", os.path.join("resources", "workflow_type_keywords.json")))
                except Exception:
                    pass  # Fallback to local path only
            
            keywords_found = False
            for path in keyword_paths:
                if os.path.exists(path):
                    try:
                        with open(path, "r") as f:
                            self.workflow_type_keywords = json.load(f)
                        keywords_found = True
                        logging.debug(f"Successfully loaded workflow keywords from: {path}")
                        break
                    except Exception as e:
                        logging.error(f"Error reading keywords file {path}: {str(e)}")
                        continue
                        
            if not keywords_found:
                logging.error("Workflow type keywords file not found. Analysis will be incomplete.")
                print("⚠️  Warning: Workflow type keywords file not found. Stage type classification will be limited.")
                self.workflow_type_keywords = {
                    "merge_write": [], "insert_write": [], "scan": [], 
                    "transform": [], "join": [], "indexing": [], 
                    "metadata": [], "clustering_compaction": []
                }
        except Exception as e:
            logging.error(f"Error loading workflow type keywords: {str(e)}")
            self.workflow_type_keywords = {
                "merge_write": [], "insert_write": [], "scan": [], 
                "transform": [], "join": [], "indexing": [], 
                "metadata": [], "clustering_compaction": []
            }
    
    def get_headers(self) -> Dict[str, Any]:
        """Get the headers for the API request."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        return headers
    
    def _request_with_retry(self, method: Callable, url: str, **kwargs) -> requests.Response:
        """Make a request with manual retry logic for cases not covered by the session adapter."""
        max_manual_retries = 2 
        retry_delay = 1
        
        for retry_count in range(max_manual_retries + 1):
            try:
                response = method(url, **kwargs)
                return response
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if retry_count < max_manual_retries:
                    logging.debug(f"Request to {url} failed with {type(e).__name__}. Retrying in {retry_delay}s... (Attempt {retry_count + 1}/{max_manual_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logging.error(f"Request to {url} failed after {max_manual_retries} retries: {str(e)}")
                    raise
            except Exception as e:
                logging.error(f"Request to {url} failed with unexpected error: {str(e)}")
                raise
    
    def _ensure_api_path(self, url: str) -> str:
        """Ensure the URL contains the Spark API path (/api/v1)."""
        if url.endswith('/'):
            url = url[:-1]
        
        logging.debug(f"Normalizing URL: {url}")
        if url.endswith('/api/v1'):
            logging.debug(f"URL already has /api/v1 suffix: {url}")
            return url
            
        if '/api/v1/' in url:
            logging.debug(f"URL already contains /api/v1/ within path: {url}")
            return url
            
        final_url = url + "/api/v1"
        logging.debug(f"Final URL with API path: {final_url}")
        return final_url
        
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request to the specified endpoint."""
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        api_base_url = self._ensure_api_path(self.base_url)
        url = f"{api_base_url}{endpoint}"
        
        logging.debug(f"Making API request to endpoint: {endpoint}")
        logging.debug(f"Full URL: {url}")
        
        try:
            logging.debug(f"Making request to: {url}")
            
            kwargs = {"timeout": self.timeout}
            
            if hasattr(self, 'cookie_dict') and self.cookie_dict:
                kwargs["cookies"] = self.cookie_dict
                if "databricks.com" in url:
                    kwargs["headers"] = {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "User-Agent": "Spark-Analyzer/1.0"
                    }
                
                if hasattr(self, 'args') and self.args and hasattr(self.args, 'debug') and self.args.debug:
                    logging.debug(f"Using cookies: {list(self.cookie_dict.keys())}")
                    logging.debug(f"Cookie count: {len(self.cookie_dict)}")
            else:
                kwargs["headers"] = self.headers if self.headers else {}
                if hasattr(self, 'args') and self.args and hasattr(self.args, 'debug') and self.args.debug:
                    logging.debug("No cookies found, using headers only")
                
            response = self._request_with_retry(self.session.get, url, **kwargs)
            response.raise_for_status()
            
            if hasattr(self, 'args') and self.args and hasattr(self.args, 'debug') and self.args.debug:
                logging.debug(f"Response status: {response.status_code}")
                logging.debug(f"Response headers: {dict(response.headers)}")
                logging.debug(f"Response content (first 500 chars): {response.text[:500]}")
            
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error for {endpoint}: {str(e)}")
                
                # Log additional debug information
                if hasattr(self, 'args') and self.args and hasattr(self.args, 'debug') and self.args.debug:
                    logging.debug(f"Response status code: {response.status_code}")
                    logging.debug(f"Response headers: {dict(response.headers)}")
                    logging.debug(f"Response content (first 1000 chars): {response.text[:1000]}")
                
                user_url = self.original_url if hasattr(self, 'original_url') else "unknown"
                
                if "console.aws.amazon.com" in user_url or "aws.amazon.com" in user_url:
                    print_error_box(
                        "AWS CONSOLE URL DETECTED",
                        f"You entered an AWS console URL: {user_url}",
                        "1. This is not a Spark History Server URL\n"
                        "2. You need the Spark History Server URL from your EMR cluster\n"
                        "3. Find it in the EMR console under your cluster's 'Application history' tab\n"
                        "4. The URL should look like: http://your-cluster-master:18080"
                    )
                    sys.exit(1)
                elif "databricks.com" in user_url and "sparkui" in user_url:
                    logging.warning(f"Databricks API returned non-JSON response for {endpoint}. This may indicate session timeout, rate limiting, or server issues.")
                    raise ValueError(f"Databricks API returned non-JSON response for {endpoint}. Response status: {response.status_code}. This may indicate session timeout, rate limiting, or server issues.")
                elif "localhost" in user_url or "127.0.0.1" in user_url:
                    print_error_box(
                        "LOCAL SPARK HISTORY SERVER ERROR",
                        f"Could not connect to local Spark History Server: {user_url}",
                        "1. Make sure Spark History Server is running on your local machine\n"
                        "2. Check if the port is correct (default is 18080)\n"
                        "3. Try accessing the URL in your browser first\n"
                        "4. If using a different port, update your URL accordingly"
                    )
                    sys.exit(1)
                else:
                    logging.warning(f"Server at {user_url} returned non-JSON response for {endpoint}. Status: {response.status_code}")
                    raise ValueError(f"Server returned non-JSON response for {endpoint}. Status: {response.status_code}. Response preview: {response.text[:200]}")
            
        except requests.exceptions.ConnectionError as e:
            if hasattr(self, 'args') and self.args and hasattr(self.args, 'debug') and self.args.debug:
                logging.error(f"Connection error for URL {url}: {e}")
            
            print_error_box(
                "CONNECTION ERROR",
                "Could not connect to the Spark History Server",
                "1. Check that the server is running and accessible\n" +
                "2. Verify your network connection\n" +
                "3. Check your server URL configuration\n" +
                f"4. Try accessing {self.original_url} in your browser\n"
            )
            
            sys.exit(1)
        except requests.exceptions.Timeout as e:
            if hasattr(self, 'args') and self.args and hasattr(self.args, 'debug') and self.args.debug:
                logging.error(f"Request timeout for {endpoint}: {e}")
            
            print_error_box(
                "CONNECTION TIMEOUT",
                f"The request to the Spark History Server timed out after {self.timeout} seconds",
                "1. Try running the command again later\n" +
                "2. The server might be processing a large amount of data\n" +
                "3. Network conditions might be causing delays\n" +
                "4. If you know the application ID, use --app_id option"
            )
            
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            
            if status_code == 404:
                logging.error(f"⚠️  Could not connect to Spark History Server at {self.original_url}")
            else:
                logging.error(f"HTTP error {status_code} for {endpoint}: {e}")
            
            if status_code == 401 or status_code == 403:
                title = f"AUTHENTICATION ERROR ({status_code})"
                message = "Server authentication failed"
                help_text = "1. Check your authentication credentials\n" + \
                           "2. Update your browser cookies if using browser mode\n" + \
                           "3. Try logging in again to the Spark History Server in your browser\n" + \
                           ("4. For AWS EMR: ensure your IAM permissions are correct\n" if "amazonaws.com" in self.base_url else "")
            elif status_code == 404:
                title = f"SPARK HISTORY SERVER NOT FOUND"
                message = f"The requested resource was not found: {endpoint}"
                help_text = "1. Verify your Spark History Server URL is correct\n" + \
                           "2. Check that the application ID or stage ID is correct"
            elif status_code == 429:
                title = f"TOO MANY REQUESTS ({status_code})"
                message = "The server is rate limiting your connections"
                help_text = "1. Wait a few minutes and try again\n" + \
                           "2. Reduce the frequency of your requests"
            elif status_code >= 500:
                title = f"SERVER ERROR ({status_code})"
                message = "The Spark History Server encountered an internal problem"
                help_text = "1. Wait a few minutes and try again\n" + \
                           "2. The server might be overloaded or experiencing issues\n" + \
                           "3. If persistent, contact your Spark admin"
            else:
                title = f"HTTP ERROR ({status_code})"
                message = f"Unexpected HTTP error: {str(e)}"
                help_text = "1. Try again later\n" + \
                           "2. Check your server URL and parameters"
            
            print_error_box(title, message, help_text)
            
            sys.exit(1)
        except json.JSONDecodeError:
            logging.error(f"JSON decode error for {endpoint}")
            
            # Determine the type of error based on the URL
            user_url = self.original_url if hasattr(self, 'original_url') else "unknown"
            
            if "console.aws.amazon.com" in user_url or "aws.amazon.com" in user_url:
                print_error_box(
                    "AWS CONSOLE URL DETECTED",
                    f"You entered an AWS console URL: {user_url}",
                    "1. This is not a Spark History Server URL\n"
                    "2. You need the Spark History Server URL from your EMR cluster\n"
                    "3. Find it in the EMR console under your cluster's 'Application history' tab\n"
                    "4. The URL should look like: http://your-cluster-master:18080"
                )
            elif "databricks.com" in user_url and "sparkui" in user_url:
                print_error_box(
                    "DATABRICKS SPARK UI URL DETECTED",
                    f"You entered an incorrect Databricks Spark UI URL",
                    "1. This is a web UI URL, not an API URL\n"
                    "2. Copy the entire Spark UI URL you see in your browser\n"
                    "3. Example format: https://dbc-xxx.cloud.databricks.com/sparkui/application-id/driver-id?o=workspace-id\n"
                    "4. Make sure you have valid Databricks cookies configured"
                )
            elif "localhost" in user_url or "127.0.0.1" in user_url:
                print_error_box(
                    "LOCAL SPARK HISTORY SERVER ERROR",
                    f"Could not connect to local Spark History Server: {user_url}",
                    "1. Make sure Spark History Server is running on your local machine\n"
                    "2. Check if the port is correct (default is 18080)\n"
                    "3. Try accessing the URL in your browser first\n"
                    "4. If using a different port, update your URL accordingly"
                )
            else:
                print_error_box(
                    "INVALID SERVER RESPONSE",
                    f"The server at {user_url} returned a non-JSON response",
                    "1. Verify you're connecting to a Spark History Server API endpoint\n"
                    "2. Make sure you're not connecting to a web UI (use --browser flag for web UIs)\n"
                    "3. Check if the server URL is correct\n"
                    "4. Try accessing the URL in your browser to verify it's accessible"
                )
            
            sys.exit(1)
    
    def get_applications(self) -> Dict[str, Any]:
        """Get all applications."""
        logging.debug("Fetching applications list")
        try:
            apps = self._make_request("/applications")
            logging.debug(f"Found {len(apps)} applications")
            return apps
        except Exception as e:
            logging.error(f"Failed to get applications: {str(e)}")
            raise

    def _get_application_attempts(self, app_id: str) -> Optional[Dict[str, Any]]:
        logging.debug(f"Fetching attempts for application {app_id}")
        try:
            clean_app_id = app_id.strip()
            attempts = self._make_request(f"/applications/{clean_app_id}")
            logging.debug(f"Found {len(attempts.get('attempts', []))} attempts for application {app_id}")
            return attempts
        except Exception as e:
            logging.debug(f"Failed to get attempts for {app_id}: {str(e)}")
            return None

    def _get_latest_attempt_id(self, app_id: str) -> Optional[str]:
        if app_id in self._app_attempt_cache:
            return self._app_attempt_cache[app_id]
        
        try:
            attempts_data = self._get_application_attempts(app_id)
            if not attempts_data or 'attempts' not in attempts_data:
                self._app_attempt_cache[app_id] = None
                return None
            
            attempts = attempts_data['attempts']
            if not attempts:
                self._app_attempt_cache[app_id] = None
                return None
            
            if len(attempts) == 1:
                attempt_id = str(attempts[0].get('attemptId', 0))
                if attempt_id == "0":
                    self._app_attempt_cache[app_id] = None
                    return None
                else:
                    logging.debug(f"Single attempt with ID {attempt_id} for {app_id}")
                    self._app_attempt_cache[app_id] = attempt_id
                    return attempt_id
            
            latest_attempt = max(attempts, key=lambda x: x.get('attemptId', 0))
            latest_attempt_id = str(latest_attempt.get('attemptId', 0))
            
            logging.debug(f"Latest attempt ID for {app_id}: {latest_attempt_id}")
            self._app_attempt_cache[app_id] = latest_attempt_id
            return latest_attempt_id
        except Exception as e:
            logging.warning(f"Error getting latest attempt ID for {app_id}: {str(e)}")
            self._app_attempt_cache[app_id] = None
            return None

    def _build_app_endpoint(self, app_id: str, endpoint: str) -> str:
        """Build API endpoint with attempt ID if needed."""
        clean_app_id = app_id.strip()
        
        attempt_id = self._get_latest_attempt_id(clean_app_id)
        
        if attempt_id:
            endpoint_path = f"/applications/{clean_app_id}/{attempt_id}{endpoint}"
            logging.debug(f"Using attempt ID {attempt_id} for {clean_app_id}: {endpoint_path}")
            return endpoint_path
        else:
            endpoint_path = f"/applications/{clean_app_id}{endpoint}"
            logging.debug(f"No attempt ID needed for {clean_app_id}: {endpoint_path}")
            return endpoint_path

    def clear_attempt_cache(self):
        self._app_attempt_cache.clear()
        logging.debug("Cleared application attempt cache")
    
    def get_executor_metrics(self, app_id: str) -> Dict[str, Any]:
        """Get executor metrics for a specific application."""
        logging.debug(f"Fetching executor metrics for application {app_id}")
        try:
            endpoint = self._build_app_endpoint(app_id, "/executors")
            metrics = self._make_request(endpoint)
            logging.debug(f"Found {len(metrics)} executor metrics entries")
            return metrics
        except Exception as e:
            logging.error(f"Failed to get executor metrics for {app_id}: {str(e)}")
            raise
    
    def get_all_executor_metrics(self,app_id: str) -> Dict[str, Any]:
        """Get all executor metrics for all applications."""
        logging.debug(f"Fetching all executor metrics for application {app_id}")
        try:
            endpoint = self._build_app_endpoint(app_id, "/allexecutors")
            metrics = self._make_request(endpoint)
            logging.debug(f"Found {len(metrics)} total executor metrics entries")
            return metrics
        except Exception as e:
            logging.error(f"Failed to get all executor metrics for {app_id}: {str(e)}")
            raise
    
    def get_application_environment(self, app_id: str) -> Dict[str, Any]:
        """Get the environment for a specific application."""
        logging.debug(f"Fetching environment for application {app_id}")
        try:
            endpoint = self._build_app_endpoint(app_id, "/environment")
            env = self._make_request(endpoint)
            logging.debug(f"Successfully retrieved environment for {app_id}")
            return env
        except Exception as e:
            logging.error(f"Failed to get environment for {app_id}: {str(e)}")
            raise
    
    def get_stage_details(self, app_id: str, stage_id: str) -> Dict[str, Any]:
        """Get details for a specific stage."""
        logging.debug(f"Fetching details for stage {stage_id} in application {app_id}")
        try:
            clean_stage_id = str(stage_id).strip()
            endpoint = self._build_app_endpoint(app_id, f"/stages/{clean_stage_id}?details=false")
            details = self._make_request(endpoint)
            logging.debug(f"Successfully retrieved details for stage {stage_id}")
            return details
        except Exception as e:
            logging.error(f"Failed to get stage details for {app_id}/{stage_id}: {str(e)}")
            raise
    
    def check_stage_exists(self, app_id: str, stage_id: str) -> bool:
        logging.debug(f"Checking if stage {stage_id} exists in application {app_id}")
        try:
            clean_stage_id = str(stage_id).strip()
            endpoint = self._build_app_endpoint(app_id, f"/stages/{clean_stage_id}?details=false")
            
            api_base_url = self._ensure_api_path(self.base_url)
            url = f"{api_base_url}{endpoint}"
            
            logging.debug(f"Making validation request to: {url}")
            
            kwargs = {"timeout": self.timeout}
            
            if hasattr(self, 'cookie_dict') and self.cookie_dict:
                kwargs["cookies"] = self.cookie_dict
                if "databricks.com" in url:
                    kwargs["headers"] = {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "User-Agent": "Spark-Analyzer/1.0"
                    }
            else:
                kwargs["headers"] = self.headers if self.headers else {}
            
            response = self._request_with_retry(self.session.get, url, **kwargs)
            response.raise_for_status()
            
            # If we get here, the stage exists
            logging.debug(f"Stage {stage_id} exists (status: {response.status_code})")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logging.debug(f"Stage {stage_id} not found (404)")
                return False
            else:
                logging.debug(f"HTTP error {e.response.status_code} for stage {stage_id}: {e}")
                return False
        except Exception as e:
            logging.debug(f"Error checking stage {stage_id}: {str(e)}")
            return False
    
    def get_stage_details_with_tasks(self, app_id: str, stage_id: str) -> Dict[str, Any]:
        """Get details for a specific stage with tasks."""
        logging.debug(f"Fetching details with tasks for stage {stage_id} in application {app_id}")
        try:
            clean_stage_id = str(stage_id).strip()
            endpoint = self._build_app_endpoint(app_id, f"/stages/{clean_stage_id}?details=true")
            details = self._make_request(endpoint)
            
            if details and isinstance(details, list) and len(details) > 0:
                stage_attempt = details[0]
                
                if "tasks" not in stage_attempt or not stage_attempt["tasks"]:
                    logging.debug(f"No task data found for stage {stage_id} - this is normal for stages that are queued or just starting")
                    return details
            
            logging.debug(f"Successfully retrieved details with tasks for stage {stage_id}")
            return details
        except Exception as e:
            logging.error(f"Failed to get stage details with tasks for {app_id}/{stage_id}: {str(e)}")
            raise
    
    def get_stages(self, app_id: str) -> Dict[str, Any]:
        """Get all stages for a specific application."""
        logging.debug(f"Fetching all stages for application {app_id}")
        try:
            endpoint = self._build_app_endpoint(app_id, "/stages")
            stages = self._make_request(endpoint)
            logging.debug(f"Found {len(stages)} stages for application {app_id}")
            return stages
        except Exception as e:
            logging.error(f"Failed to get stages for {app_id}: {str(e)}")
            raise
    
    def get_stage(self, app_id: str, stage_id: str) -> Dict[str, Any]:
        """Get a specific stage from an application."""
        return self.get_stage_details(app_id, stage_id) 