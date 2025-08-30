import git
import typer
from pathlib import Path

from rich.progress import Progress, SpinnerColumn, TextColumn

from blocks_cli.api import api_client
from blocks_cli.commands.__base__ import blocks_cli
from blocks_cli.package import warn_current_package_version
from blocks_cli.config.config import config
from blocks_cli.console import console
from blocks_cli.fs import find_dir

class AlreadyInitializedError(Exception):
    pass

@blocks_cli.command()
def init(apikey: str = typer.Option(None, "--key", help="API key for authentication")):
    """Initialize blocks in the current directory."""
    try:
        warn_current_package_version()

        # finds .blocks directory already inside or .blocks is below the current directory
        blocks_dir = find_dir(target=".blocks")

        if blocks_dir is not None:
            if apikey:
                console.print(f"[yellow]To change your API key, use [white]blocks configure --key {apikey}[/white][/yellow]")
            raise AlreadyInitializedError(f"Blocks is already initialized: [white]{blocks_dir}[/white]")
        else:
                # We are in some other subdirectory
            working_dir = Path.cwd()
            try:
                # Try to find the root of the directory if git is initialized
                repo = git.Repo(search_parent_directories=True)
                working_dir = repo.working_dir
            except Exception as e:
                pass

            # working_dir is equal to root of the directory or the current directory if git is not initialized
            working_dir = Path(working_dir)
            blocks_dir = working_dir / ".blocks"
            if not blocks_dir.exists():
                blocks_dir.mkdir()
                console.print(f"[green]Created [white].blocks[/white] folder: [white]{blocks_dir}[/white][/green]")
            else:
                if apikey:
                    console.print(f"[yellow]To change your API key, use [white]blocks configure --key {apikey}[/white][/yellow]")
                raise AlreadyInitializedError(f"[yellow]Blocks is already initialized: [white]{blocks_dir}[/white][/yellow]")

        # Verify and save API key if provided
        if apikey:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=False,
            ) as progress:
                api_task = progress.add_task(description="Verifying API key...", total=None, style="blue")

                response = api_client.get(f"{config.clients.client_url}/v1/apikeys/{apikey}", headers={
                    "Authorization": f"ApiKey {apikey}"
                })

                if response.status_code > 299:
                    raise Exception("API Key is invalid. Please check your API key at [white]https://app.blocksorg.com[/white]")
                
                config.auth.save_api_key(apikey)
                last_digits = apikey[-8:]
                progress.update(api_task, description=f"[green]API key verified and saved successfully [italic][dim]...{last_digits}[/dim][/italic][/green]")
                progress.refresh()

        console.print("[green]Blocks has been successfully initialized.[/green]")

    except AlreadyInitializedError as e:
        console.print(f"[yellow]{str(e)}[/yellow]")
        raise typer.Exit(code=0)
    except Exception as e:
        console.print(f"[red]{str(e)}[/red]")
        raise typer.Exit(code=1)
