from typing import Optional
import git
import typer
import re

from pathlib import Path
from rich.progress import Progress, SpinnerColumn, TextColumn

from blocks_cli.console import console
from blocks_cli.api import api_client
from blocks_cli.bundles import get_bundle_upload_url, upload_bundle_zip
from blocks_cli.config.config import config
from blocks_cli.commands.__base__ import blocks_cli
from blocks_cli.builds import poll_build_status
from blocks_cli.registration import get_blocks_state_and_module_from_file
from blocks_cli.package import warn_current_package_version

@blocks_cli.command()
def push(
    file: Path = typer.Argument(..., help="Name of blocks file to push."),
    bump: Optional[str] = typer.Option(
        None,
        "--bump",
        flag_value="patch",
        help="Bump version for public automations. Options: major, minor, patch. Defaults to patch if no value provided.",
    ),
    force_build: bool = typer.Option(False, "--force-build", help="Force a new build even if a successful build already exists")
):
    try:
        warn_current_package_version()

        bump_type = None
        if bump is not None:
            bump_val = bump.lower()
            if bump_val not in ("major", "minor", "patch"):
                raise Exception(
                    f"Invalid bump type '{bump}'. Valid options are: major, minor, patch"
                )
            bump_type = bump_val
            console.print(
                f"[yellow]Version bump requested: {bump_type} (applies to public automations only)[/yellow]"
            )

        # Create automation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as init_progress:
            init_task = init_progress.add_task(description="Initializing...", total=None)

            state, _ = get_blocks_state_and_module_from_file(file)

            if not state.automations:
                raise Exception(f"No automations found in the specified file")

            automation_names = []
            try:
                automation_names = [automation.get("task_kwargs",{})["name"] for automation in state.automations]
            except Exception as e:
                raise Exception("Automations must have a name defined in the [white]@task[/white] decorator")

            for automation_name in automation_names:
                is_valid = re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$", automation_name)
                if is_valid is None:
                    raise Exception(f"[red]Automation [white]'{automation_name}'[/white] is not a valid name. Automation names must start with a letter or number and can only contain letters, numbers, dashes, and underscores.[/red]")

            trigger_aliases = []
            try:
                trigger_aliases = [automation.get("trigger_alias") for automation in state.automations]
            except Exception as e:
                raise Exception("Event must be defined in the [white]@on[/white] decorator")

            for trigger_alias in trigger_aliases:
                if trigger_alias is None or trigger_alias == "":
                    raise Exception(f"Event [white]'{trigger_alias}'[/white] is not a valid. For a list of supported events, please visit [white]https://docs.blocksorg.com/docs/events[/white]")

            # working directory from where the command was invoked
            cwd = file.resolve().parent

            git_remote_url = None

            try:
                repo = git.Repo(search_parent_directories=True)
                git_remote_url = repo.remotes.origin.url if repo.remotes else None
            except Exception as e:
                pass

            requirements_path = str((cwd / "requirements.txt").resolve())
            bundle_upload = get_bundle_upload_url()

            bundle_id = bundle_upload.get("bundle_id")
            bundle_upload_url = bundle_upload.get("bundle_upload_url")

            init_progress.update(
                init_task, total=1, description="Bundle uploaded successfully"
            )
            upload_bundle_zip(bundle_upload_url, cwd, cwd.parent)
            init_progress.update(
                init_task, total=1, description="Bundle uploaded successfully"
            )

            # get pip dependencies
            pip_dependencies = []
            if Path(requirements_path).exists():
                with open(requirements_path, "r") as f:
                    pip_dependencies = f.read().splitlines()

            init_progress.update(
                init_task, total=1, description="Collecting automations..."
            )

        # Construct payload
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as upload_progress:
            upload_task = upload_progress.add_task(
                description="Uploading automation...", total=None
            )

            registration_payload = {
                "git_remote_url": git_remote_url,
                "pip_dependencies": pip_dependencies,
                "bundle_id": bundle_id,
                "automations": [],
                "force_build": force_build,
            }
            if bump_type is not None:
                registration_payload["bump_type"] = bump_type

            for automation in state.automations:
                trigger_kwargs = automation.get("trigger_kwargs", {})
                task_kwargs = automation.get("task_kwargs", {})

                automation_name = task_kwargs.get("name")

                # compute resource fields
                runner = task_kwargs.get("runner")
                vcpus = task_kwargs.get("vcpus")
                memory = task_kwargs.get("memory")
                gpu_count = task_kwargs.get("gpu_count")
                gpu_type = task_kwargs.get("gpu_type")
                runtime = task_kwargs.get("runtime") # e.x. "python3.10"
                plugins = task_kwargs.get("plugins", [])
                required_env_vars = task_kwargs.get("required_env_vars", [])

                repos: list = trigger_kwargs.get("repos", [])

                if len(repos) == 0 and git_remote_url:
                    repos.append(git_remote_url)

                function_name = automation.get("function_name")
                function_source_code = automation.get("function_source_code")
                function_hash = automation.get("function_hash")
                function_arg_count = automation.get("function_arg_count")
                function_kwarg_count = automation.get("function_kwarg_count")
                function_kwargs_info = automation.get("function_kwargs_info")
                config_schema = automation.get("config_class").model_json_schema() if automation.get("config_class") else None
                trigger_alias = automation.get("trigger_alias")

                # Extract known fields
                automation_config = {
                    "name": automation_name,
                    "function_hash": function_hash,
                    "function_source_code": function_source_code,
                    "function_arg_count": function_arg_count,
                    "function_kwarg_count": function_kwarg_count,
                    "function_kwargs_info": function_kwargs_info,
                    "import_path": f"{file.name}:{function_name}",
                    "runner": runner,
                    "runtime": runtime,
                    "plugins": plugins,
                    "required_env_vars": required_env_vars,
                    "vcpus": vcpus,
                    "memory": memory,
                    "gpu_count": gpu_count,
                    "gpu_type": gpu_type,
                    "config_schema": config_schema,
                    "trigger_alias": trigger_alias,
                    "trigger_kwargs": {},
                    "task_kwargs": {},
                }

                # Add any additional args that weren't explicitly handled
                additional_task_kwargs = {
                    k: v
                    for k, v in task_kwargs.items()
                    if k not in [
                        "vcpus", 
                        "memory_mib", 
                        "gpu_count", 
                        "gpu_type", 
                        "name", 
                        "runtime", 
                        "runner", 
                        "config_class", 
                        "plugins", 
                        "config_schema",
                        "required_env_vars"
                    ]
                }
                automation_config["trigger_kwargs"] = trigger_kwargs
                automation_config["task_kwargs"] = additional_task_kwargs
                
                registration_payload["automations"].append(automation_config)

        # Register automation
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
        ) as registration_progress:
            registration_task = registration_progress.add_task(
                description="Registering automation...", total=None
            )
            res = api_client.post(
                f"{config.clients.client_url}/v1/register", json=registration_payload
            )
            # TODO add error handling
            res.raise_for_status()
            registration_progress.update(
                registration_task, total=1, description="Automation registered successfully"
            )

        # Verify build status
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as build_progress:
            build_task = build_progress.add_task(
                description="Building automation... This may take several minutes.",
                total=None,
            )
            build_id = res.json().get("build_id")
            image_id = res.json().get("image_id")
            is_build_triggered = res.json().get("is_build_triggered")
            if is_build_triggered:
                try:
                    poll_build_status(image_id, build_id)
                    build_progress.update(
                        build_task, total=1, description="Build succeeded"
                    )
                except Exception as e:
                    error_message = str(e)
                    build_progress.update(
                        build_task, total=1, description="Build failed"
                    )
                    console.print(f"[red]Error: {error_message}[/red]")
                    console.print("[yellow]Please check your automation's requirements.txt to ensure all dependencies are valid and/or our status page at https://status.blocksorg.com[/yellow]")
                    raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]{str(e)}[/red]")
        raise typer.Exit(1)