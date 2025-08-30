import git
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from pathlib import Path

from blocks_cli.api import api_client
from blocks_cli.commands.__base__ import blocks_cli
from blocks_cli.config.config import config
from blocks_cli.console import console
from blocks_cli.registration import get_blocks_state_and_module_from_file
from blocks_cli.package import warn_current_package_version

def invoke_automation_with_test_event(automation_module, automation):
    trigger_alias = automation.get("trigger_alias")
    function_name = automation.get("function_name")

    automation_name = automation.get("task_kwargs",{}).get("name")

    # get the function from the module
    function = getattr(automation_module, function_name)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=False,
    ) as test_event_progress:
        test_event_task = test_event_progress.add_task(description="Preparing automation...", total=None)
        if trigger_alias is None or trigger_alias == "":
            raise Exception("Event must be defined in the [white]@on[/white] decorator. For a list of supported events, please visit [white]https://docs.blocksorg.com/docs/events[/white]")
        res = api_client.get(f"{config.clients.client_url}/v1/test_events", params={
            "trigger_alias": trigger_alias,
        })
        test_event_progress.update(test_event_task, description="[green]Automation ready[/green]")
        res.raise_for_status()

    event_response = res.json()
    event_data = event_response.get("event_data")

    console.print(f"[blue]Invoking automation [white]{automation_name}[/white] with event [white]{trigger_alias}[/white][/blue]")
    console.print(
        Rule("BEGIN Automation Logs", characters="=", style="blue")
    )

    res = function(event_data)
    console.print(
        Rule("END Automation Logs", characters="=", style="blue")
    )

    console.print(f"[green]Automation [white]{automation_name}[/white] invoked successfully[/green]")

       

@blocks_cli.command()
def test(
        file: Path = typer.Argument(..., help="Name of blocks file to test."),
        name: str = typer.Option(None, help="Name of the automation to test."),
    ):
    try:
        warn_current_package_version()

        state, automation_module = get_blocks_state_and_module_from_file(file)
        automations = state.automations

        num_automations = len(automations)

        if num_automations == 1:
            automation = automations[0]

            if name and automation.get("task_kwargs",{}).get("name") != name:
                raise Exception(f"Automation with name {name} not found.")

            invoke_automation_with_test_event(automation_module, automation)

        elif num_automations > 1 and not name:
            raise Exception("Multiple automations found in the file, please specify which one to test with the [white]--name[/white] flag.")
        elif num_automations > 1 and name:
            # find in automations
            automation = next((a for a in automations if a.get("task_kwargs",{}).get("name") == name), None)
            if not automation:
                raise Exception(f"Automation with name [white]{name}[/white] not found.")
            
            invoke_automation_with_test_event(automation_module, automation)
        else:
            raise Exception("No valid automations found in the specified file.")
        
    except Exception as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)
