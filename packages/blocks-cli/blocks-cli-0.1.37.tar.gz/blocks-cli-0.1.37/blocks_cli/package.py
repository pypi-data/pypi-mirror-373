import requests

from blocks_cli.config.config import config
from blocks_cli.builds import api_client
from blocks_cli.console import console

def get_current_sdk_version():
    from importlib.metadata import version
    return version('blocks-sdk')

def get_latest_sdk_version():
    response = api_client.get(f"{config.clients.client_url}/public/v1/sdk/version?current_version={get_current_sdk_version()}")
    response.raise_for_status()
    return response.json()

def warn_current_package_version():  
    current_version = get_current_sdk_version()
    latest_version_info = get_latest_sdk_version()

    latest_version = latest_version_info.get("latest_version")
    is_update_available = latest_version_info.get("is_update_available")
    is_update_required = latest_version_info.get("is_update_required")
    message = latest_version_info.get("message")

    if is_update_required:
        console.print(f"[red]:error: Update required: You are using blocks-sdk [green]{current_version}[/green] the is before the minimum required version. The latest version is [green]{latest_version}[/green]. There may be breakage, please update.[/red]")
        if message:
            console.print(message)
    elif is_update_available:
        console.print(f"[yellow]:warning: Update available: You are using blocks-sdk [green]{current_version}[/green]. The latest version is [green]{latest_version}[/green].[/yellow]")
        if message:
            console.print(message)
