# Blocks CLI

A CLI tool for Blocks, a platform for writing custom AI-enabled codebase automations in Python. Leverage a full codebase-aware API. Automatically trigger automations from GitHub, Slack, and other providers.

Status: Private alpha. Please keep your SDK updated to get the latest fixes and features.

## Prerequisites

- Python >= 3.9
- `pip` available in your environment

## Installation

Blocks CLI is packaged with the Python SDK.

```bash
pip install blocks-sdk
```

Verify installation:

```bash
blocks --help
```

## Quick Start

1) Initialize in your repository (creates a `.blocks` directory and optionally saves your API key):

```bash
# Option A: Provide key now
blocks init --key <your-api-key>

# Option B: Initialize, then configure later
blocks init
blocks configure --key <your-api-key>
```

2) Create a new automation scaffold:

```bash
blocks create my_automation
```

This generates `.blocks/my_automation/` with a starter `main.py` and `requirements.txt`.

3) Edit the generated automation to set an event and repository:

```python
# .blocks/my_automation/main.py
from blocks import task, on

@task(name="my_automation")
@on("github.pull_request", repos=["MyOrg/MyRepo"])
def my_automation(event):
    print(event)
```

4) Test the automation locally with a sample event:

```bash
blocks test .blocks/my_automation/main.py
# If your file defines multiple automations, specify one by name:
# blocks test .blocks/my_automation/main.py --name my_automation
```

5) Push the automation to Blocks:

```bash
blocks push .blocks/my_automation/main.py
```

## Command Reference

- `blocks init [--key <api-key>]`: Initializes Blocks in the current repo by creating a `.blocks` directory. When `--key` is provided, verifies and saves your API key.
- `blocks configure --key <api-key>`: Verifies and saves/updates your API key.
- `blocks create <name>`: Creates a new automation under `.blocks/<name>/` with a starter template and `requirements.txt`.
- `blocks test <file> [--name <automation>]`: Loads the automation from `<file>`, fetches a sample event for the configured trigger, and invokes it locally.
- `blocks push <file>`: Packages dependencies and source, uploads the bundle, registers the automation, and triggers a build.

## Naming Rules

- Automation names must start with a letter and can include letters, numbers, dashes, and underscores.
- Example valid names: `my_automation`, `code-reviewer`, `build_123`.

## Troubleshooting

- Already initialized: If `.blocks` exists, `blocks init` will report it. Use `blocks configure --key <api-key>` to update your key.
- Invalid API key: Ensure your key is correct. You can manage keys at https://app.blocksorg.com
- Missing event: The `@on("...")` decorator must specify a supported event. See events at https://docs.blocksorg.com/docs/events
- Multiple automations in a file: Use `--name <automation>` with `blocks test` to choose one.

## Upgrading

```bash
pip install -U blocks-sdk
```

## License

AGPL-3.0. See `LICENSE` for details.
