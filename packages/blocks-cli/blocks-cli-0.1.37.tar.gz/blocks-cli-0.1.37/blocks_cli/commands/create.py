import re
import typer
from pathlib import Path
from rich.panel import Panel

from blocks_cli.console import console
from blocks_cli.commands.__base__ import blocks_cli
from blocks_cli.fs import find_dir
from blocks_cli.package import warn_current_package_version, get_latest_sdk_version

class InvalidAutomationNameError(Exception):
    pass

class NoBlocksDirError(Exception):
    pass

class AutomationAlreadyExistsError(Exception):
    pass

@blocks_cli.command()
def create(
    name: str = typer.Argument(..., help="Name of the automation to create."),
):
    """
    Create a new automation in the .blocks directory.
    The command will fail if .blocks directory doesn't exist.
    """
    try:
        warn_current_package_version()

        # Validate automation name (only allow alphanumeric, dash, and underscore)
        if not name or re.search(r'[^a-zA-Z0-9\_-]', name) or name[0].isdigit():
            raise InvalidAutomationNameError("Automation name cannot start with a number, and must contain only letters, numbers, dashes, and underscores")

        blocks_dir = find_dir(target=".blocks")

        if not blocks_dir:
            raise NoBlocksDirError("No .blocks directory found, have you run [white]blocks init[/white]?")

        # Create automation directory
        automation_dir = blocks_dir / name
        if automation_dir.exists():
            raise AutomationAlreadyExistsError(f"Automation [white]{name}[/white] already exists")

        try:
            # Create directory and files
            automation_dir.mkdir(parents=True)

            function_name = name.replace("-", "_")
            
            # Create main.py with basic template
            with open(automation_dir / 'main.py', 'w') as f:
                f.write('''from blocks import task, on

@task(name="{name}")
@on("", repos=[])
def {function_name}(input):
    print(input)
'''.format(name=name, function_name=function_name))

            sdk_version = get_latest_sdk_version()
            latest_version = sdk_version.get("latest_version")

            with open(automation_dir / 'requirements.txt', 'w') as f:
                f.write('''blocks-sdk>={version}'''.format(version=latest_version))

            console.print(f"Successfully created automation [green]{name}[/green] in [green]{automation_dir.absolute()}[/green]")
            console.print(f"[green]{name}/\n   main.py\n   requirements.txt[/green]")
            console.print(f"[blue]Choose an event from [white]https://docs.blocksorg.com/events[/white] and run [white]blocks test .blocks/{name}/main.py[/white] to test the automation[/blue]")

        except Exception as e:
            # Clean up if something goes wrong after directory creation
            if automation_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(automation_dir)
                except Exception:
                    pass
            raise
        
    except (InvalidAutomationNameError, NoBlocksDirError, AutomationAlreadyExistsError) as e:
        console.print(f"[red]{str(e)}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error creating automation: {str(e)}[/red]")
        raise typer.Exit(1)