#!/usr/bin/env python3
import os
import sys
import logging
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich import print as rprint
from typing import Optional
import configparser
import requests
from pathlib import Path
import time
import subprocess
from typer.models import OptionInfo
from urllib.parse import urlparse, urljoin

app = typer.Typer(help="Spark Analyzer Configuration Tool")
console = Console()

def setup_logging(debug=False):
    """Setup logging configuration."""
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

from .utils.formatting import print_error_box

def test_history_server_url(url: str) -> bool:
    """Test connection to Spark History Server using curl, matching setup.sh behavior."""
    console.print("")
    try:
        # Use curl with same flags as setup.sh, but use PIPE for stdout only
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", f"{url}/applications"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # equivalent to 2>/dev/null
            text=True,
            check=False  # don't raise on non-zero exit codes
        )
        
        if result.stdout.strip() == "200":
            console.print("[green]✅ Successfully connected to Spark History Server[/green]")
            return True
        else:
            print_error_box(
                "SPARK HISTORY SERVER NOT FOUND",
                f"Could not connect to Spark History Server at {url}",
                "> 1. Verify your Spark History Server URL is correct\n"
                "> 2. Check that the server is running and accessible\n"
                "> 3. Try accessing the URL in your browser\n"
                "> 4. If using a custom path, make sure it's correct\n"
                "> 5. Check your network connection and any VPN settings"
            )
            return False
    except subprocess.CalledProcessError:
        print_error_box(
            "SPARK HISTORY SERVER NOT FOUND",
            f"Could not connect to Spark History Server at {url}",
            "> 1. Verify your Spark History Server URL is correct\n"
            "> 2. Check that the server is running and accessible\n"
            "> 3. Try accessing the URL in your browser\n"
            "> 4. If using a custom path, make sure it's correct\n"
            "> 5. Check your network connection and any VPN settings"
        )
        return False
    except FileNotFoundError:
        print_error_box(
            "CURL NOT FOUND",
            "The curl command is not available on your system",
            "> 1. Install curl on your system\n"
            "> 2. For macOS: brew install curl\n"
            "> 3. For Linux: apt-get install curl or yum install curl"
        )
        return False

def parse_databricks_url(url: str) -> tuple[str, str]:
    from urllib.parse import urlparse, urljoin
    
    if '?' in url:
        url = url.split('?')[0]
    
    parsed = urlparse(url)
    
    path_components = parsed.path.split('/')
    
    filtered_components = [comp for comp in path_components if comp and comp != 'compute']
    
    truncated_components = []
    for comp in filtered_components:
        truncated_components.append(comp)
        if comp.startswith('driver-'):
            break
    
    clean_path = '/' + '/'.join(truncated_components)

    base_url = f"{parsed.scheme}://{parsed.netloc}{clean_path}"
    
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    
    api_url = f"{base_url}/api/v1"
    
    return base_url, api_url

def extract_databricks_app_id(url: str) -> Optional[str]:
    from urllib.parse import urlparse
    
    if '?' in url:
        url = url.split('?')[0]
    
    parsed = urlparse(url)
    
    path_components = parsed.path.split('/')
    
    filtered_components = [comp for comp in path_components if comp and comp != 'compute']
    
    if len(filtered_components) >= 3 and filtered_components[0] == 'sparkui':
        app_id = filtered_components[1]
        if '-' in app_id and app_id.replace('-', '').replace('_', '').isalnum():
            return app_id
    
    return None

def extract_databricks_driver_id(url: str) -> Optional[str]:
    from urllib.parse import urlparse
    
    if '?' in url:
        url = url.split('?')[0]
    
    parsed = urlparse(url)
    
    path_components = parsed.path.split('/')
    
    filtered_components = [comp for comp in path_components if comp and comp != 'compute']
    
    if len(filtered_components) >= 3 and filtered_components[0] == 'sparkui':
        for comp in filtered_components:
            if comp.startswith('driver-'):
                driver_id = comp[7:]
                if driver_id.isdigit():
                    return driver_id
    
    return None

def get_available_editor():
    """Get available text editor for editing cookies file."""
    editors = ['vim', 'nano', 'code', 'subl']
    for editor in editors:
        if subprocess.run(['which', editor], capture_output=True, check=False).returncode == 0:
            return editor
    return None

@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    config_dir: Optional[str] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory to store configuration files"
    ),
    opt_out: Optional[str] = typer.Option(
        None,
        "--opt-out",
        help="Comma-separated list of fields to opt out of (name,description,details)"
    ),
    save_local: bool = typer.Option(
        False,
        "--save-local",
        help="Save analysis data locally instead of uploading to Onehouse"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug logging (DEBUG level, includes all requests/responses)"
    ),
    live_app: bool = typer.Option(
        False,
        "--live-app",
        help="Indicate this is a live/running application (enables reverse processing and stage validation to handle race conditions)"
    )
):
    # Setup logging based on debug flag
    setup_logging(debug)
    if debug:
        logging.debug("Debug logging enabled")
    """Spark Analyzer Configuration Tool."""
    if ctx.invoked_subcommand is None:
        # If no subcommand was specified, run configure with the provided arguments
        ctx.invoke(configure, config_dir=config_dir, opt_out=opt_out, save_local=save_local, debug=debug, live_app=live_app)

@app.command()
def configure(
    config_dir: Optional[str] = None,
    opt_out: Optional[str] = None,
    save_local: bool = False,
    debug: bool = False,
    live_app: bool = False
):
    """Interactive configuration for Spark Analyzer."""
    if isinstance(config_dir, OptionInfo):
        config_dir = None
    
    console.print("[bold blue]==============================================[/bold blue]")
    console.print("[bold blue]       Spark Analyzer Configuration Wizard    [/bold blue]")
    console.print("[bold blue]==============================================[/bold blue]")
    console.print("")
    
    if config_dir is not None:
        config_dir = Path(config_dir)
    else:
        config_dir = Path.home() / ".spark_analyzer"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.ini"
    
    # Cost Estimator User ID
    console.print("[bold blue]Cost Estimator User ID (Optional):[/bold blue]")
    console.print("Enter your ID for enhanced analysis features including cost estimation.")
    console.print("[dim]Get your cost estimator ID from Onehouse: Visit https://www.onehouse.ai/spark-analysis-tool to get your user ID[/dim]")
    console.print("")
    console.print("Press Enter to skip for local-only analysis.")
    console.print("")
    
    cost_estimator_id = Prompt.ask(
        "\nEnter your Cost Estimator User ID",
        default=""
    )

    if cost_estimator_id:
        console.print(f"[green]✓ Cost Estimator ID configured: {cost_estimator_id}[/green]")
        console.print("   You can now get enhanced analysis features including cost estimation.")
    else:
        console.print("[yellow]⚠ No Cost Estimator ID provided.[/yellow]")
        console.print("   You can still run the tool using --save-local mode for local analysis.")
        console.print("   To add this later, run 'spark-analyzer configure' again.")
        console.print("")
        console.print("   [bold]What this means:[/bold]")
        console.print("   • Without ID: Use 'spark-analyzer analyze --save-local' for local analysis (basic reports)")
        console.print("   • With ID: Get enhanced analysis, cost estimation, and optimization reports")
    
    # Connection Mode
    console.print("")
    console.print("[bold blue]Connection Mode:[/bold blue]")
    console.print("1) Local mode (direct connection to Spark History Server)")
    console.print("2) Browser mode (connects through browser cookies for EMR, Databricks, or other web-based applications)")
    
    while True:
        connection_mode = Prompt.ask(
            "\nChoose connection mode",
            choices=["1", "2"],
            default="1"
        )
        if connection_mode not in ["1", "2"]:
            console.print("")
            console.print("[red]Error: Invalid option. Please choose 1 or 2[/red]")
            console.print("")
            continue
        break
    
    # History Server URL
    if connection_mode == "1":
        console.print("")
        console.print("[bold blue]Spark History Server URL:[/bold blue]")
        console.print("Enter the full URL to your Spark History Server.")
        console.print("Examples:")
        console.print("  - Standard local: http://localhost:18080")
        console.print("  - Port forwarded: http://localhost:8080/onehouse-spark-code/history-server")
        console.print("  - Live application: http://localhost:4040")
        
        while True:
            history_server_url = Prompt.ask(
                "\nEnter Spark History Server URL",
                default="http://localhost:18080"
            )
            
            # If user just pressed Enter, use default
            if not history_server_url:
                console.print("")
                console.print("[yellow]Using default URL: http://localhost:18080[/yellow]")
                console.print("")
                history_server_url = "http://localhost:18080"
            
            # Validate URL format
            if not history_server_url.startswith(("http://", "https://")):
                console.print("")
                console.print("[red]Error: URL must start with http:// or https://[/red]")
                console.print("Please enter a valid URL (e.g., http://localhost:18080)")
                console.print("Or press Enter to use the default URL: http://localhost:18080")
                console.print("")
                continue
            
            # Process URL
            history_server_url = history_server_url.rstrip("/")
            if not history_server_url.endswith("/api/v1"):
                history_server_url = f"{history_server_url}/api/v1"
    
            # Test connection
            if test_history_server_url(history_server_url):
                break
    elif connection_mode == "2":
        history_server_url = "browser_mode_placeholder"
    
    # Create config file
    config = _create_config_file(history_server_url, cost_estimator_id, live_app, connection_mode)
    
    with open(config_file, "w") as f:
        config.write(f)
    
    console.print(f"\n[green]✅ Configuration saved to {config_file}[/green]")
    
    # Handle browser mode cookies
    if connection_mode == "2":
        _setup_browser_cookies(config_dir, history_server_url)

    # Ask if user wants to run now
    run_immediately = Confirm.ask("\nWould you like to run the analyzer now?")
    
    console.print("")
    
    if not run_immediately:
        console.print("💡 Tip: Your configuration is still saved and ready to use.")
        console.print("   You can run the analyzer later with: spark-analyzer")
    
    return run_immediately

def _create_config_file(history_server_url, cost_estimator_id, live_app, connection_mode):
    """Create the configuration object with all required settings."""
    config = configparser.ConfigParser()
    
    # Only save base_url for local mode
    if connection_mode == "1":  # Local mode
        config["server"] = {"base_url": history_server_url}
    # For browser mode, don't save URL (will be collected at runtime)
    
    if cost_estimator_id:
        config["cost_estimator"] = {"user_id": cost_estimator_id}

    config["processing"] = {"live_app": str(live_app).lower()}
    config["connection"] = {"mode": "local" if connection_mode == "1" else "browser"}
    return config

def _setup_browser_cookies(config_dir, history_server_url):
    """Set up browser cookies for browser mode."""
    # Removed all the detailed cookie setup information
    # Users will get this information at runtime when needed
    pass



@app.command()
def show():
    """Show current configuration."""
    config_dir = Path.home() / ".spark_analyzer" # Use home directory for configuration
    config_file = config_dir / "config.ini"
    
    if not config_file.exists():
        print_error_box(
            "CONFIGURATION NOT FOUND",
            f"No configuration file found at {config_file}",
            "Run 'spark-analyzer configure' to set up your configuration"
        )
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    console.print("[bold blue]Current Configuration:[/bold blue]")
    console.print("=" * 50)
    
    for section in config.sections():
        console.print(f"\n[bold]{section}[/bold]")
        for key, value in config[section].items():
            console.print(f"  {key}: {value}")
    
    # Only show cookie status for local mode
    connection_mode = config.get('connection', 'mode', fallback='local')
    if connection_mode == 'local':
        console.print("\n[bold]Local Mode:[/bold]")
        console.print("  Status: [green]Configured[/green]")
        console.print("  Note: Direct connection to Spark History Server")
    else:
        console.print("\n[bold]Browser Mode:[/bold]")
        console.print("  Status: [green]Configured[/green]")
        console.print("  Note: URLs and cookies collected at runtime for security")

if __name__ == "__main__":
    app() 