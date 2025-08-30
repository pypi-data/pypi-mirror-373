#!/usr/bin/env python3
import sys
import os
import argparse
import logging
import json
import tabulate
import time
import requests
import tqdm
import datetime
import configparser
import subprocess

from .lib.api_client import APIClient
from .lib.spark_stage_analyzer import SparkStageAnalyzer
from .lib.s3_uploader import S3Uploader
from .utils.formatting import print_error_box
from .config_cli import extract_databricks_driver_id, extract_databricks_app_id
from rich.console import Console

# Create console instance for rich formatting
console = Console()

def setup_logging(verbose=False, debug=False):
    """Set up logging with appropriate verbosity level"""
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.CRITICAL
    
    class TqdmLoggingHandler(logging.Handler):
        def emit(self, record):
            if record.name == 'urllib3.connectionpool' and 'Retrying' in record.getMessage():
                return
            if 'Failed to establish a new connection' in record.getMessage():
                return
            if 'Invalid URL' in record.getMessage():
                return
            if 'No host supplied' in record.getMessage():
                return
            if 'Failed to parse' in record.getMessage():
                return
            if 'Cookie format may be invalid' in record.getMessage():
                return
            try:
                msg = self.format(record)
                tqdm.tqdm.write(msg)
            except Exception:
                self.handleError(record)
    
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    log_format = '%(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format)
    
    handler = TqdmLoggingHandler()
    handler.setFormatter(formatter)
    
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    
    return logging.getLogger(__name__)

def parse_analyze_arguments():
    parser = argparse.ArgumentParser(
        description='Analyze Spark applications',
        add_help=True
    )
    parser.add_argument('-l', '--local', action='store_true', 
                        help='Run in local mode (overrides saved configuration)')
    parser.add_argument('-b', '--browser', action='store_true',
                        help='Run in browser mode (overrides saved configuration)')
    parser.add_argument('-s', '--stage_id', type=str, default=None,
                        help='Stage ID to analyze')
    parser.add_argument('-a', '--app_id', type=str, default=None,
                        help='Application ID to analyze')
    parser.add_argument('--opt-out', type=str, default="",
                        help='Comma-separated list of fields to opt out of (name,description,details)')
    parser.add_argument('--upload-url', type=str, default=None,
                        help='URL to upload the JSON output to (will use gzip compression)')
    parser.add_argument('--save-local', action='store_true',
                        help='Save analysis data locally instead of uploading to S3 (creates JSON files in spark_analysis_output directory)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose logging (INFO level)')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debug logging (DEBUG level, includes all requests/responses)')
    parser.add_argument('--env', type=str, choices=['staging', 'production'], default='production',
                        help='Environment to use (staging requires SPARK_ANALYZER_STAGING_* env vars, production is default)')
    parser.add_argument('--cost-estimator-id', type=str, default=None,
                        help='Cost estimator user ID (overrides saved configuration)')
    parser.add_argument('--server-url', type=str, default=None,
                        help='Custom Spark History Server URL (overrides saved configuration)')
    parser.add_argument('--batch-size', type=int, default=50,
                        help='Number of stages to process in each batch (default: 50)')
    parser.add_argument('--live-app', action='store_true',
                        help='Indicate this is a live/running application (enables reverse processing and stage validation to handle race conditions)')
    
    return parser

def parse_configure_arguments():
    parser = argparse.ArgumentParser(
        description='Configure Spark Analyzer',
        add_help=True
    )
    parser.add_argument('--opt-out', type=str, default="",
                        help='Comma-separated list of fields to opt out of (name,description,details)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode for configuration')
    parser.add_argument('--save-local', action='store_true',
                        help='Configure to save analysis data locally instead of uploading to S3')
    
    return parser

def parse_report_arguments():
    parser = argparse.ArgumentParser(
        description='Generate acceleration report from analysis data',
        add_help=True
    )
    parser.add_argument('--input', '-i', required=True,
                        help='Input JSON file containing Spark diagnostics payload or analysis output')
    parser.add_argument('--output', '-o',
                        help='Output file for the report (default: auto-generated based on input)')
    parser.add_argument('--output-dir', '-d',
                        help='Output directory for batch processing')
    parser.add_argument('--format', '-f', choices=['excel'], default='excel',
                        help='Output format for the report (Excel only)')

    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    
    return parser

def parse_arguments():
    if len(sys.argv) == 1:
        return 'analyze', parse_analyze_arguments().parse_args([])
    
    if len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        sys.exit(0)
    
    if len(sys.argv) >= 2:
        command = sys.argv[1]
        
        if command == 'analyze':
            analyze_parser = parse_analyze_arguments()
            analyze_args = sys.argv[2:]
            
            if '--help' in analyze_args or '-h' in analyze_args:
                analyze_parser.print_help()
                sys.exit(0)
            
            args = analyze_parser.parse_args(analyze_args)
            return 'analyze', args
        
        elif command == 'configure':
            configure_parser = parse_configure_arguments()
            configure_args = sys.argv[2:]
            
            if '--help' in configure_args or '-h' in configure_args:
                configure_parser.print_help()
                sys.exit(0)
            
            args = configure_parser.parse_args(configure_args)
            return 'configure', args
        
        elif command == 'report':
            report_parser = parse_report_arguments()
            report_args = sys.argv[2:]
            
            if '--help' in report_args or '-h' in report_args:
                report_parser.print_help()
                sys.exit(0)
            
            args = report_parser.parse_args(report_args)
            return 'report', args
        
        elif command == 'readme':
            return 'readme', None

        elif command in ['-h', '--help', 'help']:
            show_help()
            sys.exit(0)
        
        else:
            print(f"Unknown command: {command}")
            show_help()
            sys.exit(1)
    
    return 'analyze', parse_analyze_arguments().parse_args([])

def show_help():
    print("Spark Analyzer - Spark Application Analysis Tool")
    print("=" * 50)
    print()
    print("Usage:")
    print("  spark-analyzer                    # Default: runs analyze command")
    print("  spark-analyzer analyze            # Explicit analyze command")
    print("  spark-analyzer analyze --local    # Run in local mode")
    print("  spark-analyzer analyze --browser  # Run in browser mode")
    print("  spark-analyzer configure          # Run configuration wizard")
    print("  spark-analyzer report             # Generate acceleration report")
    print("  spark-analyzer readme             # Show the README documentation")
    print()
    print("Commands:")
    print("  analyze     Analyze Spark applications (default command)")
    print("  configure   Run configuration wizard to set up or modify settings")
    print("  report      Generate acceleration report from analysis data")
    print("  readme      Show the README documentation")
    print()
    print("For detailed help on a command:")
    print("  spark-analyzer analyze --help")
    print("  spark-analyzer configure --help")
    print("  spark-analyzer report --help")
    print()
    print("Examples:")
    print("  spark-analyzer                    # Run with saved configuration")
    print("  spark-analyzer analyze --local    # Run in local mode")
    print("  spark-analyzer analyze --browser  # Run in browser mode")
    print("  spark-analyzer configure          # Run configuration wizard")
    print("  spark-analyzer configure --opt-out name,description,details")
    print("  spark-analyzer report --input data.json --output report.xlsx")

def upload_output(data: dict, upload_url: str) -> bool:
    """Upload JSON data to the specified URL using gzip compression."""
    try:
        json_data = json.dumps(data)
        headers = {
            'Content-Type': 'application/json',
            'Content-Encoding': 'gzip',
            'Accept-Encoding': 'gzip'
        }
        
        logging.debug(f"Uploading data to {upload_url} (size: {len(json_data)} bytes)")
        
        response = requests.post(
            upload_url,
            data=json_data,
            headers=headers,
            stream=True
        )
        
        response.raise_for_status()
        logging.info(f"Successfully uploaded to {upload_url}")
        return True
        
    except requests.exceptions.ConnectionError as e:
        print_error_box(
            "CONNECTION ERROR", 
            f"Could not connect to {upload_url}",
            f"Check your internet connection\nVerify the URL is correct and accessible"
        )
        logging.debug(f"Connection error details: {str(e)}")
        return False
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        print_error_box(
            f"HTTP ERROR {status_code}", 
            f"Server returned error: {e.response.text[:200]}",
            f"Check if the URL is correct\nVerify you have permission to upload to this endpoint"
        )
        logging.debug(f"HTTP error details: {str(e)}")
        return False
    except Exception as e:
        print_error_box(
            "UPLOAD ERROR", 
            f"Error uploading data: {str(e)}",
            "Try again later or use a different upload method"
        )
        logging.debug(f"Upload error details: {str(e)}")
        return False

def get_user_input(prompt: str, validator=None):
    """Get user input with validation."""
    while True:
        try:
            user_input = input(prompt).strip()
            if validator and not validator(user_input):
                continue
            return user_input
        except KeyboardInterrupt:
            # Let KeyboardInterrupt bubble up to the main handler
            raise

def save_local_output(data: dict, app_id: str, output_dir: str = "spark_analysis_output") -> bool:
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spark_analysis_{app_id}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Analysis data saved locally: {os.path.abspath(filepath)}")
        logging.info(f"Successfully saved analysis data to {filepath}")
        return True
        
    except Exception as e:
        print_error_box(
            "LOCAL SAVE ERROR",
            f"Failed to save analysis data locally: {str(e)}",
            "Check write permissions for the output directory\nEnsure sufficient disk space is available"
        )
        logging.debug(f"Local save error details: {str(e)}")
        return False

def process_app_id(app_id, applications, client, spark_stage_analyzer, s3_uploader, args, s3_upload_enabled, processed_app_ids, successful_upload_app_ids, failed_upload_app_ids, summary_app_ids, app_index=0, app_count=1):
    print(f"\n🔄 Processing application {app_id} ({app_index + 1}/{app_count})...")
    application_name = next((app['name'] for app in applications if app['id'] == app_id), None)
    if application_name:
        print(f"📝 Application name: {application_name}")
        
    application_start_time_ms = None
    application_end_time_ms = None
    application = next((app for app in applications if app['id'] == app_id), None)
    if not application.get('attempts'):
        raise ValueError(f"No attempts found in application {application.get('id', 'unknown')}")
    attempt = application['attempts'][0]
    application_start_time_ms = attempt.get('startTimeEpoch')
    application_end_time_ms = attempt.get('endTimeEpoch')
    logging.debug(f"Application {app_id} start time: {application_start_time_ms}, end time: {application_end_time_ms}")
    
    if len(application.get('attempts', [])) > 1:
        latest_attempt_id = client._get_latest_attempt_id(app_id)
        if latest_attempt_id:
            if args and args.debug:
                print(f"📊 Application has {len(application['attempts'])} attempts - using latest attempt ID: {latest_attempt_id}")
            logging.info(f"Application {app_id} has {len(application['attempts'])} attempts, using latest: {latest_attempt_id}")
        else:
            if args and args.debug:
                print(f"📊 Application has {len(application['attempts'])} attempts - using base application ID")
            logging.info(f"Application {app_id} has {len(application['attempts'])} attempts, using base app ID")
    elif len(application.get('attempts', [])) == 1:
        attempt_id = str(application['attempts'][0].get('attemptId', 0))
        if attempt_id != "0":
            if args and args.debug:
                print(f"📊 Application has attempt ID: {attempt_id}")
            logging.info(f"Application {app_id} has single attempt with ID: {attempt_id}")
    
    try:
        print("🔄 Fetching stages...")
        stages = client.get_stages(app_id)
        print(f"📋 Found {len(stages)} stages")
        if len(stages) == 0:
            print_error_box(
                "NO STAGES FOUND",
                f"Application {app_id} has no stages to analyze.",
                "This could be because:\n" +
                "1. The application is still running\n" +
                "2. The application hasn't started any stages yet\n" +
                "3. The application has completed but no stages were recorded\n\n" +
                "Please try analyzing a different application."
            )
            return 'zero_stages'
        if app_id not in summary_app_ids:
            summary_app_ids.append(app_id)
    except Exception as e:
        print_error_box(
            "STAGE FETCH ERROR",
            f"Failed to fetch stages for application {app_id}",
            "This application might be incomplete, still running, or there was a connection issue.\nTry analyzing a different application or check your network/server."
        )
        logging.debug(f"Stage fetch error details: {str(e)}")
        return 'connection_error'

    print("🔄 Fetching executor metrics...")
    try:
        executor_metrics = client.get_all_executor_metrics(app_id)
        print(f"📋 Found {len(executor_metrics)} executors (including historical)")
    except Exception as e:
        print_error_box(
            "EXECUTOR METRICS ERROR",
            f"Failed to fetch executor metrics for application {app_id}",
            "Proceeding with limited executor information\nSome executor details may be missing in the analysis"
        )
        logging.debug(f"Executor metrics error details: {str(e)}")
        executor_metrics = []

    total_executors = len([e for e in executor_metrics if e["id"] != "driver"])
    total_cores = sum(e.get("totalCores", 0) for e in executor_metrics if e["id"] != "driver")
    presigned_urls = None
    batch_filenames = []
    proceed_with_processing = True

    if s3_upload_enabled and len(stages) > 0 and not (os.environ.get('SPARK_ANALYZER_SAVE_LOCAL_MODE') == '1' or args.save_local):
        batch_size = 1000
        total_batches = (len(stages) + batch_size - 1) // batch_size
        print(f"🔄 Preparing {total_batches} batches for S3 upload (up to {batch_size} stages each)...")
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(stages))
            batch_range = f"{start_idx}-{end_idx-1}"
            batch_filename = f"stages_{app_id}_batch{batch_range}.json"
            batch_filenames.append(batch_filename)

        print(f"🔄 Requesting pre-signed URLs for {len(batch_filenames)} batches upfront...")
        try:
            presigned_urls = s3_uploader.get_presigned_urls(app_id, batch_filenames)
        except Exception as e:
            presigned_urls = None
            if args.debug:
                logging.debug(f"Pre-signed URL error details: {str(e)}")

        if not presigned_urls or len(presigned_urls) != len(batch_filenames):
            print_error_box(
                "UPLOAD PREPARATION ERROR",
                f"Unable to prepare analysis upload for application {app_id}",
                "Verify your cost estimator user ID is correct\nContact Onehouse support if the problem persists\nRun with --debug for more details"
            )
            if args.debug:
                logging.error(f"Failed to get pre-signed URLs: got {len(presigned_urls) if presigned_urls else 0}, expected {len(batch_filenames)}")
            print(f"The analysis could not be uploaded for application {app_id}. Please re-run the tool or contact Onehouse support if the issue persists.")
            proceed_with_processing = False
            failed_upload_app_ids.append(app_id)
        else:
            successful_upload_app_ids.append(app_id)

    if not proceed_with_processing:
        return 'upload_error'

    print("🔄 Analyzing stages and generating output...")
    proto_output = {
        "application_id": app_id,
        "total_executors": total_executors,
        "total_cores": total_cores,
        "application_start_time_ms": application_start_time_ms or 0,
        "application_end_time_ms": application_end_time_ms or 0,
        "executors": [
            {
                "executor_id": e["id"],
                "is_active": e.get("isActive", False),
                "total_cores": e.get("totalCores", 0),
                "add_time": e.get("addTime", ""),
                "remove_time": e.get("removeTime", "")
            }
            for e in executor_metrics
            if e["id"] != "driver"
        ],
        "stages": []  
    }

    if args.live_app:
        stages_sorted = sorted(stages, key=lambda x: int(x.get('stageId', 0)), reverse=True)
        print(f"🔄 Processing {len(stages_sorted)} stages in reverse order...")
        
        BATCH_SIZE = min(args.batch_size, 50)  
        print(f"🔄 Using batch size {BATCH_SIZE} for live app processing...")
    else:
        stages_sorted = sorted(stages, key=lambda x: int(x.get('stageId', 0)))
        print(f"🔄 Processing {len(stages_sorted)} stages in normal order (completed app)...")
        
        BATCH_SIZE = max(args.batch_size, 100)  
        print(f"🔄 Using batch size {BATCH_SIZE} for completed app processing...")
    
    total_batches = (len(stages_sorted) + BATCH_SIZE - 1) // BATCH_SIZE
    
    failed_stages = 0
    skipped_stages = 0
    
    with tqdm.tqdm(total=len(stages_sorted), desc="Processing stages", unit="stage", dynamic_ncols=True, leave=True) as pbar:
        for batch_idx in range(total_batches):
            start_idx = batch_idx * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(stages_sorted))
            batch_stages = stages_sorted[start_idx:end_idx]
            
            for stage in batch_stages:
                try:
                    stage_id = stage.get('stageId')
                    if stage_id is None:
                        logging.debug("Found stage with missing stageId, skipping")
                        skipped_stages += 1
                        pbar.update(1)
                        continue
                    
                    if args.live_app:
                        stage_exists = client.check_stage_exists(app_id, stage_id)
                        if not stage_exists:
                            logging.info(f"Stage {stage_id} not found (likely removed), skipping")
                            skipped_stages += 1
                            pbar.update(1)
                            continue
                        else:
                            logging.debug(f"Stage {stage_id} validation passed")
                    
                    stage_data = spark_stage_analyzer.format_stage_for_proto(stage, app_id, executor_metrics)
                    if stage_data:
                        proto_output["stages"].append(stage_data)
                    else:
                        failed_stages += 1
                        logging.debug(f"Stage {stage_id} processing returned None")
                        
                except ValueError as e:
                    failed_stages += 1
                    stage_id = stage.get('stageId', 'unknown')
                    error_msg = str(e)
                    
                    if "Databricks API returned non-JSON response" in error_msg:
                        logging.warning(f"Stage {stage_id}: Databricks API issue - {error_msg}")
                        if args.debug:
                            logging.debug(f"Stage {stage_id} failed due to Databricks API response issue. This may indicate session timeout or rate limiting.")
                    elif "Server returned non-JSON response" in error_msg:
                        logging.warning(f"Stage {stage_id}: Server returned non-JSON response - {error_msg}")
                        if args.debug:
                            logging.debug(f"Stage {stage_id} failed due to server returning non-JSON response.")
                    else:
                        logging.warning(f"Stage {stage_id}: API error - {error_msg}")
                        if args.debug:
                            logging.debug(f"Stage {stage_id} failed due to API error: {error_msg}")
                    
                    pbar.update(1)
                    continue
                        
                except Exception as e:
                    failed_stages += 1
                    stage_id = stage.get('stageId', 'unknown')
                    logging.warning(f"Stage {stage_id}: Unexpected error - {str(e)}")
                    if args.debug:
                        logging.debug(f"Stage {stage_id} failed due to unexpected error: {str(e)}")
                        import traceback
                        logging.debug(f"Exception traceback: {traceback.format_exc()}")
                
                pbar.update(1)
            
            if args.live_app and batch_idx < total_batches - 1:
                time.sleep(1)

    if failed_stages > 0:
        print(f"⚠️  {failed_stages} stages encountered errors and were skipped")
        logging.info(f"Failed stages for application {app_id}: {failed_stages} out of {len(stages)}")
    
    if skipped_stages > 0 and args.live_app:
        print(f"⚠️  {skipped_stages} stages were skipped (likely removed during live app processing)")
        logging.info(f"Skipped stages for live application {app_id}: {skipped_stages} out of {len(stages)}")
    elif skipped_stages > 0:
        print(f"⚠️  {skipped_stages} stages were skipped due to processing errors")
        logging.info(f"Skipped stages for application {app_id}: {skipped_stages} out of {len(stages)}")

    if os.environ.get('SPARK_ANALYZER_SAVE_LOCAL_MODE') == '1' or args.save_local:
        success = save_local_output(proto_output, app_id)
        if success:
            successful_upload_app_ids.append(app_id)
        else:
            failed_upload_app_ids.append(app_id)
    elif s3_upload_enabled and presigned_urls and len(presigned_urls) == len(batch_filenames):
        for presigned_url in presigned_urls:
            json_data = json.dumps(proto_output)
            success = s3_uploader.upload_json_data(presigned_url, json_data)
            if not success:
                logging.error(f"Failed to upload {batch_filename} to S3")

        success = s3_uploader.signal_application_completion(app_id, batch_filenames)
        if not success:
            print(f"\n❌ Error: Failed to signal completion for application {app_id}. Upload may be incomplete.")
            logging.error(f"Failed to signal completion for application {app_id}")
        else:
            print(f"\n✅ Signaled completion for application {app_id}!")

    print(f"\n✅ Stage analysis complete for {app_id}!")
    processed_app_ids.append(app_id)
    
    if args and args.browser:
        clear_cookie_files(args)
    
    return 'success'

def run_analysis(args):
    """Main analysis function that orchestrates the entire process."""
    logger = setup_logging(args.verbose, args.debug)
    
    try:
        print("🚀 Spark History Server Analyzer")
        print("===============================")
        
        print("⚙️  Initializing components...")
        
        config, config_file_path, run_immediately = check_and_load_configuration(args)
        
        if not _should_continue_analysis(run_immediately, config_file_path):
            print("Configuration saved to: ~/.spark_analyzer/config.ini")
            sys.exit(0)

        if not run_immediately and not args.save_local:
            cost_estimator_id = get_cost_estimator_id_from_config(config)
            if not cost_estimator_id:
                sys.exit(0)

        if not args.local and not args.browser:
            connection_mode = get_connection_mode_from_config(config)
            if connection_mode == 'local':
                args.local = True
            elif connection_mode == 'browser':
                args.browser = True
        
        if not args.cost_estimator_id:
            args.cost_estimator_id = get_cost_estimator_id_from_config(config)
        
        if not args.server_url:
            if args.browser:
                args.server_url = None
            else:
                args.server_url = get_server_url_from_config(config)
        
        if not args.live_app:
            try:
                if 'processing' in config and 'live_app' in config['processing']:
                    try:
                        args.live_app = config.getboolean('processing', 'live_app')
                        logging.debug(f"Live app setting from config: {args.live_app}")
                    except (ValueError, configparser.Error):
                        logging.warning("Invalid live_app setting in config, using default: False")
                        args.live_app = False
                else:
                    args.live_app = False
            except Exception as e:
                logging.debug(f"Could not read live_app from config: {str(e)}")
                args.live_app = False
        
        if args.server_url:
            client = APIClient(base_url=args.server_url, args=args)
            if args.debug:
                print(f"ℹ️  Using custom server URL: {args.server_url}")
        else:
            client = APIClient(args=args)
        
        if args.browser and not args.server_url:
            print("\n🌐 Browser Mode - Runtime Configuration Required")
            print("Since you're using browser mode, we need to collect the URL and cookies now.")
            print("")
            
            console.print("[bold blue]How to get the Spark History Server URL:[/bold blue]")
            console.print("")
            console.print("[bold]For Databricks:[/bold]")
            console.print("1. Open your Databricks workspace in your browser")
            console.print("2. Navigate to the Spark UI for your application")
            console.print("3. Click 'Open in new tab' in the Spark UI")
            console.print("4. Copy the entire URL from the new tab")
            console.print("")
            console.print("[bold]For EMR:[/bold]")
            console.print("1. Open the EMR console in your browser")
            console.print("2. Navigate to the Spark History Server URL")
            console.print("3. Copy the URL from your browser's address bar")
            console.print("")
            
            while True:
                url_input = get_user_input("Enter Spark History Server URL: ")
                if url_input.strip():
                    if "databricks.com" in url_input or "azuredatabricks.net" in url_input:
                        if "sparkui" in url_input:
                            try:
                                from .config_cli import parse_databricks_url
                                base_url, api_url = parse_databricks_url(url_input)
                                args.server_url = api_url
                                print(f"✅ Parsed Databricks URL: {api_url}")
                                break
                            except Exception as e:
                                print(f"❌ Error parsing Databricks URL: {str(e)}")
                                print("Please check the URL format and try again.")
                                continue
                        else:
                            print("⚠️  Databricks URL should contain 'sparkui' in the path")
                            print("Please copy the link from the Spark UI 'Open in new tab' option")
                            continue
                    else:
                        url_input = url_input.rstrip("/")
                        if not url_input.endswith("/api/v1"):
                            url_input = f"{url_input}/api/v1"
                        args.server_url = url_input
                        print(f"✅ Using URL: {url_input}")
                        break
                else:
                    print("❌ URL is required for browser mode")
                    continue
            
            client = APIClient(base_url=args.server_url, args=args)
            
            print("\n🍪 Cookie Authentication Required")
            print("You need to provide browser cookies for authentication.")
            print("")
            
            console.print("[bold blue]How to get browser cookies:[/bold blue]")
            console.print("")
            console.print("[bold]For Databricks:[/bold]")
            console.print("1. Open your Databricks workspace in your browser")
            console.print("2. Navigate to the Spark UI for your application")
            console.print("3. Open developer tools (F12 or right-click > Inspect)")
            console.print("4. Go to the Network tab and click on any request")
            console.print("5. Find the 'Cookie' header in the Request Headers")
            console.print("6. Copy the entire cookie string")
            console.print("")
            console.print("[bold]For EMR or other platforms:[/bold]")
            console.print("1. Open the Spark History Server in your browser")
            console.print("2. Open developer tools (F12 or right-click > Inspect)")
            console.print("3. Go to the Network tab and click on any request")
            console.print("4. Find the 'Cookie' header in the Request Headers")
            console.print("5. Copy the entire cookie string")
            console.print("")
            console.print("[yellow]⚠️  Important:[/yellow] Cookies are collected temporarily for this session only.")
            console.print("No cookies will be saved permanently in your configuration.")
            console.print("")
            
            while True:
                cookie_input = get_user_input("Enter cookies (press Enter to edit in editor): ")
                
                if not cookie_input.strip():
                    from .config_cli import get_available_editor
                    editor = get_available_editor()
                    if editor:
                        import tempfile
                        temp_cookie_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
                        temp_cookie_file.close()
                        
                        print(f"\nOpening {editor} to edit cookies...")
                        print("Paste your cookies, save and exit the editor when done.")
                        print("")
                        
                        try:
                            subprocess.run([editor, temp_cookie_file.name], check=True)
                            with open(temp_cookie_file.name, 'r') as f:
                                cookie_input = f.read().strip()
                            
                            os.unlink(temp_cookie_file.name)
                            
                            if cookie_input:
                                print("✅ Cookies loaded from editor")
                                break
                            else:
                                print("❌ No cookies provided in editor")
                                print("Please provide cookies to continue.")
                                print("")
                                continue
                        except subprocess.CalledProcessError:
                            continue
                    else:
                        continue
                else:
                    break
            
            # Set cookies in the client
            if cookie_input:
                client.set_cookies_from_string(cookie_input)
                print("✅ Cookies set successfully")
            else:
                print("❌ No cookies provided")
                sys.exit(1)
        
        spark_stage_analyzer = SparkStageAnalyzer(client)
        
        use_staging = args.env == 'staging'
        s3_uploader = S3Uploader(config_file="config.ini", use_staging=use_staging, args=args)
        
        can_use_enhanced_mode = bool(args.cost_estimator_id)
        
        if args.save_local:
            os.environ['SPARK_ANALYZER_SAVE_LOCAL_MODE'] = '1'
            s3_upload_enabled = False
            print("💾 Running in local save mode - analysis data will be saved locally")
        elif can_use_enhanced_mode:
            s3_upload_enabled = True
            print("🚀 Running in enhanced mode - will attempt Onehouse upload")
        else:
            s3_upload_enabled = False
            os.environ['SPARK_ANALYZER_SAVE_LOCAL_MODE'] = '1'
            print("💾 No cost estimator ID found - running in local save mode")
            print("   Analysis data will be saved locally")
            print("   To enable enhanced features, run 'spark-analyzer configure' to add your cost estimator ID")

        opt_out_fields = set()
        if args.opt_out:
            opt_out_fields = set(args.opt_out.split(","))
            spark_stage_analyzer.set_opt_out_fields(opt_out_fields)
            logging.info(f"Using opt-out fields: {opt_out_fields}")

        app_ids = []
        applications = None
        
        if args.app_id:
            app_ids = [args.app_id]
            logging.info(f"Using provided application ID: {args.app_id}")
        else:
            is_databricks = (
                ("databricks.com" in client.base_url and "sparkui" in client.base_url) or
                ("azuredatabricks.net" in client.base_url and "sparkui" in client.base_url) or
                (hasattr(client, 'original_url') and "databricks.com" in client.original_url and "sparkui" in client.original_url) or
                (hasattr(client, 'original_url') and "azuredatabricks.net" in client.original_url and "sparkui" in client.original_url)
            )
            
            if is_databricks:
                print(f"🔍 Detected Databricks URL - fetching application data...")
                logging.info("Detected Databricks URL, fetching application data")
                
                try:
                    logging.debug("Fetching applications data for Databricks")
                    applications = client.get_applications()
                    logging.debug(f"Fetched {len(applications) if applications else 0} applications for Databricks")
                    
                    if applications and len(applications) > 0:
                        app_id = applications[0]['id']
                        app_ids = [app_id]
                        print(f"✅ Found application: {app_id}")
                        
                        # Check if this application has multiple attempts
                        if len(applications[0].get('attempts', [])) > 1:
                            latest_attempt_id = client._get_latest_attempt_id(app_id)
                            if latest_attempt_id:
                                if args and args.debug:
                                    print(f"📊 Application has {len(applications[0]['attempts'])} attempts - using latest attempt ID: {latest_attempt_id}")
                            else:
                                if args and args.debug:
                                    print(f"📊 Application has {len(applications[0]['attempts'])} attempts - using base application ID")
                        elif len(applications[0].get('attempts', [])) == 1:
                            # Check if single attempt has non-zero attempt ID
                            attempt_id = str(applications[0]['attempts'][0].get('attemptId', 0))
                            if attempt_id != "0":
                                if args and args.debug:
                                    print(f"📊 Application has attempt ID: {attempt_id}")
                                logging.info(f"Application {app_id} has single attempt with ID: {attempt_id}")
                        
                        logging.info(f"Using application ID: {app_id}")
                    else:
                        print_error_box(
                            "DATABRICKS APPLICATION NOT FOUND",
                            "No applications found in Databricks.",
                            "The application might have been deleted or the URL might be incorrect.\n" +
                            "Please check the Databricks URL."
                        )
                        sys.exit(1)
                            
                except Exception as e:
                    user_url = client.original_url if hasattr(client, 'original_url') else "unknown"
                    logging.warning(f"Failed to fetch applications data for Databricks URL: {str(e)}")
                    print_error_box(
                        "DATABRICKS API ERROR",
                        f"Failed to fetch applications from: {user_url}",
                        "1. Please check your Databricks cookies and try again\n"
                        "2. Make sure you're logged into Databricks in your browser\n"
                        "3. Verify the Databricks URL is correct"
                    )
                    sys.exit(1)
            else:
                try:
                    print("🔄 Fetching available applications...")
                    max_app_fetch_retries = 1
                    fetch_attempt = 0
                    
                    print("⏳ Connecting to Spark History Server...")
                    
                    while fetch_attempt < max_app_fetch_retries:
                        try:
                            applications = client.get_applications()
                            break
                        except requests.exceptions.ConnectionError as e:
                            fetch_attempt += 1
                            if fetch_attempt < max_app_fetch_retries:
                                retry_delay = 2 ** fetch_attempt
                                logging.debug(f"Connection error - retrying in {retry_delay}s (attempt {fetch_attempt}/{max_app_fetch_retries})")
                                if fetch_attempt == 1:
                                    print("⚠️  Connection to server failed, retrying...")
                                time.sleep(retry_delay)
                            else:
                                raise
                        except requests.exceptions.Timeout as e:
                            fetch_attempt += 1
                            if fetch_attempt < max_app_fetch_retries:
                                retry_delay = 2 ** fetch_attempt
                                logging.debug(f"Timeout error - retrying in {retry_delay}s (attempt {fetch_attempt}/{max_app_fetch_retries})")
                                if fetch_attempt == 1:
                                    print("⚠️  Server response timed out, retrying...")
                                time.sleep(retry_delay)
                            else:
                                raise

                    if not applications:
                        print_error_box(
                            "NO APPLICATIONS FOUND",
                            "No applications were found in the Spark History Server",
                            "Check if the Spark History Server has any applications\n"
                            "Verify your connection settings\n"
                            "Make sure Spark History Server is running and accessible\n"
                            "If using browser mode, verify your cookies are valid\n"
                            "If using Databricks mode, verify your Databricks cookies are valid"
                        )
                        sys.exit(1)

                    if len(applications) == 0:
                        print("⚠️  The Spark History Server contains no applications.")
                        print("   You need to specify an application ID manually.")
                        while True:
                            app_to_analyze = get_user_input("\n🔍 Enter the application id(s) to analyze, separated by commas without spaces (required): ")
                            if not app_to_analyze:
                                print("\n❌ Error: Application ID is required.")
                                print("Please enter at least one application ID to proceed.")
                                continue
                            app_ids = [aid.strip() for aid in app_to_analyze.split(',') if aid.strip()]
                            if not app_ids:
                                print("\n❌ Error: No valid application IDs provided.")
                                print("Please enter at least one application ID to proceed.")
                                continue
                            break
                    else:
                        print(f"📋 Found {len(applications)} applications")
                        valid_app_ids = {app['id'] for app in applications}
                        
                        app_table = []
                        for app in applications:
                            app_id = app.get('id', 'N/A')
                            app_name = app.get('name', 'N/A')
                            attempts_count = len(app.get('attempts', []))
                            
                            # Add attempt information to the display (debug mode only)
                            if args and args.debug:
                                if attempts_count > 1:
                                    latest_attempt_id = client._get_latest_attempt_id(app_id)
                                    if latest_attempt_id:
                                        app_display = f"{app_id} (latest attempt: {latest_attempt_id})"
                                    else:
                                        app_display = f"{app_id} ({attempts_count} attempts)"
                                elif attempts_count == 1:
                                    # Check if single attempt has non-zero attempt ID
                                    attempt_id = str(app['attempts'][0].get('attemptId', 0))
                                    if attempt_id != "0":
                                        app_display = f"{app_id} (attempt: {attempt_id})"
                                    else:
                                        app_display = app_id
                                else:
                                    app_display = app_id
                            else:
                                app_display = app_id
                            
                            app_table.append([app_display, app_name])
                        
                        headers = ["Application ID", "Application Name"]
                        print("\nAvailable Applications:")
                        print(tabulate.tabulate(app_table, headers=headers, tablefmt="grid"))
                        
                        # Show a note about multiple attempts if any exist
                        multi_attempt_apps = [app for app in applications if len(app.get('attempts', [])) > 1]
                        if multi_attempt_apps and args and args.debug:
                            print("\n💡 Note: Applications with multiple attempts will automatically use the latest attempt.")
                        
                        while True:
                            app_to_analyze = get_user_input("\n🔍 Enter the application id(s) to analyze, separated by commas without spaces (required): ")
                            if not app_to_analyze:
                                print("\n❌ Error: Application ID is required.")
                                print("Please enter at least one application ID from the list above.")
                                continue
                            
                            entered_app_ids = [aid.strip() for aid in app_to_analyze.split(',') if aid.strip()]
                            if not entered_app_ids:
                                print("\n❌ Error: No valid application IDs provided.")
                                print("Please enter at least one application ID from the list above.")
                                continue
                            
                            # Handle cases where user might have entered the full display string
                            clean_app_ids = []
                            for aid in entered_app_ids:
                                # Extract just the app ID part if user entered the full display string
                                if " (latest attempt:" in aid:
                                    clean_aid = aid.split(" (latest attempt:")[0]
                                elif " (" in aid and " attempts)" in aid:
                                    clean_aid = aid.split(" (")[0]
                                else:
                                    clean_aid = aid
                                clean_app_ids.append(clean_aid)
                            
                            invalid_ids = [aid for aid in clean_app_ids if aid not in valid_app_ids]
                            if invalid_ids:
                                print(f"\n❌ Invalid application ID(s): {', '.join(invalid_ids)}")
                                print("Please enter only valid application IDs from the list above.")
                                continue
                            
                            app_ids = clean_app_ids
                            break

                except requests.exceptions.ConnectionError as e:
                    user_url = client.original_url if hasattr(client, 'original_url') else "unknown"
                    print_error_box(
                        "CONNECTION ERROR",
                        f"Failed to connect to the Spark History Server at: {user_url}",
                        "1. Check that the server is running and accessible\n"
                        "2. Verify your network connection and any VPN settings\n"
                        "3. Confirm the server URL in your configuration file\n"
                        "4. Fix the connection issue before proceeding"
                    )
                    
                    logging.debug(f"Connection error details: {str(e)}")
                    sys.exit(1)

                except requests.exceptions.Timeout as e:
                    user_url = client.original_url if hasattr(client, 'original_url') else "unknown"
                    print_error_box(
                        "CONNECTION TIMEOUT",
                        f"The request to the Spark History Server timed out: {user_url}",
                        "1. The server might be slow or processing a large amount of data\n"
                        "2. Try again later or with a longer timeout setting\n"
                        "3. Consider using port forwarding with SSH if connecting to a remote server\n"
                        "4. Fix the connection issue before proceeding"
                    )
                    
                    logging.debug(f"Timeout error details: {str(e)}")
                    sys.exit(1)

                except Exception as e:
                    # Get the original URL that the user provided
                    user_url = client.original_url if hasattr(client, 'original_url') else "unknown"
                    
                    print_error_box(
                        "APPLICATION FETCH ERROR",
                        f"Failed to fetch Spark applications",
                        "1. Check your connection settings and History Server URL\n"
                        "2. Verify the server is running and accessible\n"
                        "3. Run with --debug flag for more detailed error information\n"
                        "4. Fix the connection issue before proceeding"
                    )
                    
                    logging.debug(f"Application fetch error details: {str(e)}")
                    sys.exit(1)

        if app_ids and len(app_ids) > 0:
            skipped_zero_stage_apps = []
            processed_app_ids = []
            summary_app_ids = []
            successful_upload_app_ids = []
            failed_upload_app_ids = []

            for app_index, app_id in enumerate(app_ids):
                if app_index > 0:
                    import time
                    print("⏳ Waiting 2 seconds before processing next application...")
                    time.sleep(2)
                
                while True:
                    result = process_app_id(app_id, applications, client, spark_stage_analyzer, s3_uploader, args, s3_upload_enabled, processed_app_ids, successful_upload_app_ids, failed_upload_app_ids, summary_app_ids, app_index, len(app_ids))
                    if result == 'success':
                        break
                    elif result == 'upload_error':
                        sys.exit(1)
                    elif result == 'zero_stages':
                        while True:
                            retry = get_user_input("\nWould you like to try another application ID? (y/n): ")
                            if retry.lower().strip() in ['y', 'yes']:
                                break
                            elif retry.lower().strip() in ['n', 'no']:
                                sys.exit(0)
                            else:
                                print("\n❌ Error: Please enter 'y' for yes or 'n' for no.")
                        while True:
                            new_app_id = get_user_input("\n🔍 Enter another application ID to analyze (required): ")
                            if not new_app_id.strip():
                                print("\n❌ Error: Application ID is required.")
                                continue
                            if not any(app['id'] == new_app_id.strip() for app in applications):
                                print(f"\n❌ Error: Application {new_app_id} not found in the list of available applications.")
                                continue
                            app_id = new_app_id.strip()
                            new_result = process_app_id(new_app_id.strip(), applications, client, spark_stage_analyzer, s3_uploader, args, s3_upload_enabled, processed_app_ids, successful_upload_app_ids, failed_upload_app_ids, summary_app_ids, app_index, len(app_ids))
                            if new_result == 'zero_stages':
                                continue
                            elif new_result == 'upload_error':
                                sys.exit(1)
                            break
                        if new_result == 'success':
                            break
                        continue
                    elif result == 'connection_error':
                        while True:
                            retry = get_user_input("\nConnection error occurred. Would you like to try another application ID? (y/n): ")
                            if retry.lower().strip() in ['y', 'yes']:
                                break
                            elif retry.lower().strip() in ['n', 'no']:
                                sys.exit(0)
                            else:
                                print("\n❌ Error: Please enter 'y' for yes or 'n' for no.")
                        while True:
                            new_app_id = get_user_input("\n🔍 Enter another application ID to analyze (required): ")
                            if not new_app_id.strip():
                                print("\n❌ Error: Application ID is required.")
                                continue
                            if not any(app['id'] == new_app_id.strip() for app in applications):
                                print(f"\n❌ Error: Application {new_app_id} not found in the list of available applications.")
                                continue
                            app_id = new_app_id.strip()
                            break
                        continue
                    else:
                        break

            if skipped_zero_stage_apps:
                print("\nThe following application IDs had 0 stages and were skipped:")
                for skipped_id in skipped_zero_stage_apps:
                    print(f"  - {skipped_id}")
                print("")
                while True:
                    overall_retry = get_user_input("Would you like to re-enter a different application ID for any of the skipped apps? (y/n): ")
                    if overall_retry.lower().strip() in ['n', 'no']:
                        break
                    elif overall_retry.lower().strip() in ['y', 'yes']:
                        for skipped_id in skipped_zero_stage_apps:
                            while True:
                                retry = get_user_input(f"Would you like to re-enter a different application ID for {skipped_id}? (y/n): ")
                                if retry.lower().strip() in ['y', 'yes']:
                                    while True:
                                        new_app_id = get_user_input("\n🔍 Enter a replacement application ID to analyze (required): ")
                                        if not new_app_id.strip():
                                            print("\n❌ Error: Application ID is required.")
                                            continue
                                        if not any(app['id'] == new_app_id.strip() for app in applications):
                                            print(f"\n❌ Error: Application {new_app_id} not found in the list of available applications.")
                                            continue
                                        if new_app_id.strip() in processed_app_ids:
                                            print(f"\n❌ Error: Application {new_app_id} has already been processed.")
                                            continue
                                        print(f"\n🔄 Processing replacement application {new_app_id.strip()}...")
                                        result = process_app_id(new_app_id.strip(), applications, client, spark_stage_analyzer, s3_uploader, args, s3_upload_enabled, processed_app_ids, successful_upload_app_ids, failed_upload_app_ids, summary_app_ids, 0, 1)
                                        if result == 'zero_stages' or result == 'connection_error':
                                            continue
                                        elif result == 'upload_error':
                                            sys.exit(1)
                                        break
                                    break
                                elif retry.lower().strip() in ['n', 'no']:
                                    break
                                else:
                                    print("\n❌ Error: Please enter 'y' for yes or 'n' for no.")
                        break
                    else:
                        print("\n❌ Error: Please enter 'y' for yes or 'n' for no.")

            # Skip S3 completion signaling if in save-local mode
            if s3_upload_enabled and successful_upload_app_ids and not (os.environ.get('SPARK_ANALYZER_SAVE_LOCAL_MODE') == '1' or args.save_local):
                print("🔄 Finalizing upload process...")
                try:
                    if s3_uploader.signal_all_jobs_completion(successful_upload_app_ids):
                        print("✅ Upload finalized successfully")
                        print("\n📬 Onehouse has received and is now processing your Spark job metadata.")
                        print("📊 You will receive your custom report of Spark optimization opportunities shortly.")
                    else:
                        print("ℹ️  Upload partially complete - your data was saved but processing may be delayed")
                except Exception as e:
                    print("ℹ️  Upload partially complete - your data was saved but processing may be delayed")
                    if args.debug:
                        logging.debug(f"Completion signal error details: {str(e)}")
            
            print("\n" + "─" * 50)
            print("📋 PROCESS SUMMARY")
            print("─" * 50)
            
            print("✅ Analysis: Complete - Successfully analyzed the following Spark application(s):")
            for app_id in summary_app_ids:
                print(f"   - {app_id}")
            print("")
            if os.environ.get('SPARK_ANALYZER_SAVE_LOCAL_MODE') == '1' or args.save_local:
                if successful_upload_app_ids:
                    print(f"💾 Local Save: Data was successfully saved locally for {len(successful_upload_app_ids)} application(s):")
                    for app_id in successful_upload_app_ids:
                        print(f"   - {app_id}")
                    print("")
                if failed_upload_app_ids:
                    print(f"❌ Local Save: Data could NOT be saved locally for {len(failed_upload_app_ids)} application(s):")
                    for app_id in failed_upload_app_ids:
                        print(f"   - {app_id} (see error above)")
                    print("")
                if not failed_upload_app_ids:
                    print("✅ All data saved locally successfully.")
            elif s3_upload_enabled or args.upload_url:
                if successful_upload_app_ids:
                    print(f"✅ Upload: Data was successfully uploaded for {len(successful_upload_app_ids)} application(s):")
                    for app_id in successful_upload_app_ids:
                        print(f"   - {app_id}")
                    print("")
                if failed_upload_app_ids:
                    print(f"❌ Upload: Data could NOT be uploaded for {len(failed_upload_app_ids)} application(s):")
                    for app_id in failed_upload_app_ids:
                        print(f"   - {app_id} (see error above)")
                    print("")
                    
                    # Add recovery message for failed uploads
                    print("💡 TO FIX THE ISSUE:")
                    print("Run the configuration wizard to set the correct Cost Estimator User ID:")
                    print("")
                    print("   spark-analyzer configure")
                    print("")
                if not failed_upload_app_ids:
                    print("✅ All uploads completed successfully.")
            else:
                print("ℹ️ Upload: Not configured - No upload destinations were specified")
            print("─" * 50)
        else:
            print("\n❌ No applications selected for analysis. Exiting.")
            
    except Exception as e:
        print_error_box(
            "UNEXPECTED ERROR",
            f"An unexpected error occurred: {str(e)}",
            "Try running with --debug flag for more detailed information\nCheck your configuration and try again"
        )
        if args.debug:
            import traceback
            traceback.print_exc()
        logging.debug(f"Unexpected error details: {str(e)}")
        sys.exit(1)

def run_report(args):
    """Main report generation function that creates acceleration reports."""
    logger = setup_logging(args.verbose, args.debug)
    
    try:
        print("🚀 Spark Acceleration Report Generator")
        print("=====================================")
        
        # Import the report generator components
        try:
            from .local_analysis.report_generator import (
                get_input_files, get_output_files, generate_report
            )
        except ImportError:
            print_error_box(
                "IMPORT ERROR",
                "Failed to import report generator components",
                "Make sure the local_analysis module is available\n"
                "Check your installation and try again"
            )
            sys.exit(1)
        
        output_format = 'excel'
        
        try:
            input_files = get_input_files(args.input)
            
            output_files = get_output_files(input_files, args.output, args.output_dir)
            
            if args.verbose:
                print(f"📋 Found {len(input_files)} input file(s)")
                print(f"📁 Will generate {len(output_files)} {output_format.upper()} output file(s)")
            
            successful = 0
            failed = 0
            
            for i, (input_file, output_file) in enumerate(zip(input_files, output_files)):
                if args.verbose:
                    print(f"\n🔄 Processing file {i+1}/{len(input_files)}")
                
                success, error_msg = generate_report(input_file, output_file, output_format, args.verbose)
                if success:
                    successful += 1
                else:
                    failed += 1
                    # Always show error details, not just in verbose mode
                    print(f"❌ Failed to process {input_file}: {error_msg}")
                    if args.debug:
                        import traceback
                        traceback.print_exc()
            
            print(f"\n📊 Report Generation Summary:")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"📁 Total files processed: {len(input_files)}")
            print(f"📄 Output format: {output_format.upper()}")
            
            if failed > 0:
                sys.exit(1)
                
        except Exception as e:
            print_error_box(
                "REPORT GENERATION ERROR",
                f"Failed to generate report: {str(e)}",
                "Check your input file format and try again\n"
                "Run with --verbose for more details"
            )
            if args.debug:
                import traceback
                traceback.print_exc()
            logging.debug(f"Report generation error details: {str(e)}")
            sys.exit(1)
            
    except Exception as e:
        print_error_box(
            "UNEXPECTED ERROR",
            f"An unexpected error occurred: {str(e)}",
            "Try running with --debug flag for more detailed information\nCheck your input and try again"
        )
        if args.debug:
            import traceback
            traceback.print_exc()
        logging.debug(f"Unexpected error details: {str(e)}")
        sys.exit(1)

def show_readme():
    """Display the README documentation."""
    try:
        try:
            from importlib.resources import files
            readme_file = files('spark_analyzer').joinpath('README.md')
            readme_content = readme_file.read_text(encoding='utf-8')
        except ImportError:
            import pkg_resources
            readme_content = pkg_resources.resource_string('spark_analyzer', 'README.md').decode('utf-8')
        
        print(readme_content)
    except Exception as e:
        print_error_box(
            "README ERROR",
            f"Failed to display README: {str(e)}",
            "The README file could not be found or read.\n"
            "You can view the documentation online at:\n"
            "https://pypi.org/project/spark-analyzer/"
        )
        sys.exit(1)

def main():
    try:
        command, args = parse_arguments()
        
        if command == 'configure':
            _send_telemetry('configure_command')
            try:
                from .config_cli import configure
                run_immediately = configure(opt_out=args.opt_out, debug=args.debug, save_local=args.save_local)
                
                if run_immediately:
                    analyze_args = parse_analyze_arguments().parse_args([])
                    if hasattr(args, 'debug') and args.debug:
                        analyze_args.debug = True
                    if hasattr(args, 'save_local') and args.save_local:
                        analyze_args.save_local = True
                    run_analysis(analyze_args)
                else:
                    sys.exit(0)
                    
            except Exception as e:
                print_error_box(
                    "CONFIGURATION ERROR",
                    f"Failed to run configuration wizard: {str(e)}",
                    "Please run 'spark-analyzer configure' manually to set up your configuration"
                )
                sys.exit(1)
        
        elif command == 'analyze':
            if args.save_local:
                _send_telemetry('analyze_save_local')
            else:
                _send_telemetry('analyze_command')
            run_analysis(args)
        
        elif command == 'report':
            _send_telemetry('report_command')
            run_report(args)
        
        elif command == 'readme':
            _send_telemetry('readme_command')
            show_readme()
            sys.exit(0)

        else:
            print(f"Unknown command: {command}")
            show_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user.")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

def clear_cookie_files(args):
    """Clear cookie files after analysis to ensure fresh cookies for next run."""
    if not args or not args.browser:
        return
    
    # Determine which cookie files to clear based on the environment
    cookie_files_to_clear = []
    
    # Add environment-specific cookie files
    if hasattr(args, 'env') and args.env:
        env_suffix = f"_{args.env}" if args.env != "production" else ""
        cookie_files_to_clear.extend([
            f"~/.spark_analyzer/databricks_cookies{env_suffix}.txt",
            f"~/.spark_analyzer/raw_cookies{env_suffix}.txt"
        ])
    
    # Add default cookie files
    cookie_files_to_clear.extend([
        "~/.spark_analyzer/databricks_cookies.txt",
        "~/.spark_analyzer/raw_cookies.txt"
    ])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_cookie_files = []
    for cookie_file in cookie_files_to_clear:
        if cookie_file not in seen:
            seen.add(cookie_file)
            unique_cookie_files.append(cookie_file)
    
    cleared_files = []
    for cookie_file in unique_cookie_files:
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, 'w') as f:
                    f.write('')
                cleared_files.append(cookie_file)
                logging.debug(f"Cleared cookie file: {cookie_file}")
            except Exception as e:
                logging.debug(f"Could not clear cookie file {cookie_file}: {str(e)}")
    
    if cleared_files:
        print(f"\n🧹 Cleared {len(cleared_files)} cookie file(s) for fresh authentication on next run")
        logging.info(f"Cleared cookie files: {cleared_files}")

def check_and_load_configuration(args=None):
    """Check if configuration exists and load it, or prompt for configuration if missing."""
    config_path = os.path.expanduser("~/.spark_analyzer/config.ini")
    config = None
    config_file_path = None
    
    if os.path.exists(config_path):
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            config_file_path = config_path
        except Exception as e:
            logging.debug(f"Could not read config from {config_path}: {str(e)}")
    
    # Check if config is complete (has all required sections)
    config_complete = _is_config_complete(config, args)
    
    if not config_complete:
        return _run_configuration_wizard(config, config_file_path, args)
    
    return config, config_file_path, False

def _is_config_complete(config, args=None):
    """Check if configuration has all required sections and options."""
    if not config:
        return False
    
    # Check if we have the basic required sections
    if args and hasattr(args, 'save_local') and args.save_local:
        # For --save-local mode, cost_estimator is optional
        pass
    else:
        # For normal mode (without --save-local), cost_estimator is required
        if not config.has_section('cost_estimator') or not config.has_option('cost_estimator', 'user_id'):
            return False
    
    if not config.has_section('connection') or not config.has_option('connection', 'mode'):
        return False
    
    # For local mode, we need base_url
    # For browser mode, we don't need base_url (will prompt at runtime)
    connection_mode = config.get('connection', 'mode')
    if connection_mode == 'local':
        if not config.has_section('server') or not config.has_option('server', 'base_url'):
            return False
    
    return True

def _run_configuration_wizard(config, config_file_path, args=None):
    """Run the configuration wizard and return the result."""
    if config and config_file_path:
        print(f"🔧 Configuration file found but incomplete: {config_file_path}")
        print("")
        show_configuration_mode_selection()

        if args and hasattr(args, 'save_local') and not args.save_local:
            sys.exit(0)

        print("Starting fresh configuration...")
        try:
            os.remove(config_file_path)
        except Exception as e:
            logging.debug(f"Could not remove incomplete config: {str(e)}")
    else:
        print("🔧 Configuration not found.")
    
    print("Running configuration wizard...")
    print("")
    
    try:
        from .config_cli import configure
        run_immediately = configure()
        
        if not run_immediately:
            sys.exit(0)
        
        config_path = os.path.expanduser("~/.spark_analyzer/config.ini")
        if os.path.exists(config_path):
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            
            # Check if the configuration is complete for enhanced mode
            # Only check if we're not in save-local mode
            if run_immediately and args and hasattr(args, 'save_local') and not args.save_local:
                cost_estimator_id = get_cost_estimator_id_from_config(config)
                if not cost_estimator_id:
                    print("\n❌ Configuration incomplete for enhanced mode")
                    show_configuration_mode_selection()
                    sys.exit(0)
            
            return config, config_path, run_immediately
        else:
            return None, None, run_immediately
    except Exception as e:
        print_error_box(
            "CONFIGURATION ERROR",
            f"Failed to run configuration wizard: {str(e)}",
            "Please run 'spark-analyzer configure' manually to set up your configuration"
        )
        sys.exit(1)

def _should_continue_analysis(run_immediately, config_file_path):
    if run_immediately is True:
        return True 
    elif run_immediately is False and config_file_path:
        return True
    elif run_immediately is False:
        return False
    return True 

def get_connection_mode_from_config(config):
    """Get connection mode from configuration file."""
    if config.has_section('connection') and config.has_option('connection', 'mode'):
        return config.get('connection', 'mode')
    return 'local'  # Default to local mode

def get_cost_estimator_id_from_config(config):
    """Get cost estimator ID from configuration file."""
    if config.has_section('cost_estimator') and config.has_option('cost_estimator', 'user_id'):
        return config.get('cost_estimator', 'user_id')
    return None

def get_server_url_from_config(config):
    """Get server URL from configuration file."""
    if config.has_section('server') and config.has_option('server', 'base_url'):
        return config.get('server', 'base_url')
    return None

def show_configuration_mode_selection():
    """Display the configuration mode selection message."""
    print("Your configuration is missing the Cost Estimator User ID required for enhanced analysis features.")
    print("")
    print("Choose your analysis mode:")
    print("1. Enhanced analysis: Run 'spark-analyzer configure' to add your Cost Estimator User ID")
    print("2. Local analysis: Use 'spark-analyzer analyze --save-local' for offline analysis")
    print("3. Get your cost estimator ID from Onehouse: Visit https://www.onehouse.ai/spark-analysis-tool to sign up and get your user ID")
    print("")
    print("💡 For local analysis now: spark-analyzer analyze --save-local")
    print("💡 For enhanced features, add cost estimator user id by running: spark-analyzer configure")
    print("") 

def _send_telemetry(event_type: str):
    """Send telemetry data for command usage tracking."""
    try:
        import os
        import threading
        import requests
        import platform
        from datetime import datetime, timezone
        
        if os.getenv('SCARF_NO_ANALYTICS', '').lower() != 'true':
            def send_telemetry():
                try:
                    try:
                        import tomllib
                        with open('pyproject.toml', 'rb') as f:
                            pyproject_data = tomllib.load(f)
                        version = pyproject_data.get('project', {}).get('version', 'unknown')
                    except Exception:
                        try:
                            import pkg_resources
                            version = pkg_resources.get_distribution('spark-analyzer').version
                        except Exception:
                            version = 'unknown'

                    data = {
                        'package': 'spark-analyzer',
                        'event': event_type,
                        'command': 'configure',
                        'python_version': platform.python_version(),
                        'os': platform.system(),
                        'os_version': platform.platform(),
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                    }
                    requests.post(
                        f'https://onehouse.gateway.scarf.sh/telemetry/spark-analyzer/{event_type}',
                        json=data,
                        timeout=2,
                        headers={
                            'User-Agent': f'spark-analyzer/{version}/telemetry',
                            'Content-Type': 'application/json'
                        }
                    )
                except:
                    pass
            
            thread = threading.Thread(target=send_telemetry, daemon=True)
            thread.start()
            thread.join(timeout=3)
    except:
        pass

if __name__ == "__main__":
    main() 