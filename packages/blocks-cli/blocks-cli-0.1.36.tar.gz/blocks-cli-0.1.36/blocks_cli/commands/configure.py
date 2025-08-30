import typer
from rich.progress import Progress, SpinnerColumn, TextColumn

from blocks_cli.config.config import config
from blocks_cli.console import console
from blocks_cli.commands.__base__ import blocks_cli
from blocks_cli.package import warn_current_package_version
from blocks_cli.api import api_client
class InvalidApiKeyError(Exception):
    pass

@blocks_cli.command()
def configure(apikey: str = typer.Option(None, "--key", help="Blocks API key")):
    """Configure the blocks CLI."""
    try:
        warn_current_package_version()

        existing_api_key = config.auth.api_key
        lastDigits = existing_api_key[-8:] if existing_api_key else ""

        new_api_key = None
        if not apikey:
            console.print("Enter Blocks API Key below", end=" ")

            if lastDigits:
                console.print(
                    "[dim]leave empty if you want to keep existing API key: [/dim]",
                    style="italic",
                    end=" ",
                )
                console.print(f"[dim]...{lastDigits}[/dim]", style="italic")
            else:
                print()

            new_api_key = typer.prompt("API Key", existing_api_key, show_default=False)
        else:
            new_api_key = apikey


        if not new_api_key:
            raise InvalidApiKeyError("No API key has has been previously saved, please retry with a valid API key.")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
        ) as init_progress:
            try:
                api_task = init_progress.add_task(description="Verifying API key...", total=None)

                response = api_client.get(f"{config.clients.client_url}/v1/apikeys/{new_api_key}", headers={
                    "Authorization": f"ApiKey {new_api_key}"
                })

                if response.status_code > 299:
                    raise Exception("API Key is invalid. Please check your API key at [white]https://app.blocksorg.com[/white]")
                
                config.auth.save_api_key(new_api_key)
                last_digits = new_api_key[-8:]
                init_progress.update(api_task, description=f"[green]API key verified and saved successfully [italic][dim]...{last_digits}[/dim][/italic][/green]")
            except Exception as e:
                raise InvalidApiKeyError(f"Failed to verify API key. Please check your API key at [white]https://app.blocksorg.com[/white]")

    except InvalidApiKeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error configuring blocks[/red]")
        raise typer.Exit(code=1)
