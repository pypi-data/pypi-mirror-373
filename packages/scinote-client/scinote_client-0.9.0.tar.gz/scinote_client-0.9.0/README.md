# SciNote Client

SciNote Client is a Python library for interacting with the SciNote API. This
library allows you to programmatically manage SciNote inventories, including
creating and managing inventories, columns, items, and more.

## Installation

You can install the SciNote Client library directly from its
[official repository](https://pypi.org/project/scinote-client/) using pip:

```bash
pip install scinote-client
```

Alternatively, if you have the source code, you can install the package
locally by running:

```bash
pip install -e path/to/scinote-client-source
```

> **Note**: If you already have the official version installed, please
uninstall it before proceeding.

## Usage

The library requires 2 environment variables to be configured:

* `SCINOTE_BASE_URL` - The API endpoint
* `SCINOTE_API_KEY` - The API key, generated in the SciNote admin console.

Here's a basic example of how to use the SciNote Client:

```python
import asyncio
from scinote_client.client.api.teams_client import CreateClient

# Initialize the client
teams_client = CreateClient()

# Get a list of teams
teams = asyncio.run(teams_client.get_teams())
for team in teams:
  print(team.id)

# Get a list of inventories for a team.
inventories_client = teams_client.inventory_client(teams[0].team_id)

inventories = asyncio.run(inventories_client.get_inventories())
for inventory in inventories:
  print(inventory.id)

```



## Documentation

For detailed documentation, please refer to the [official documentation](https://scinote-eln.github.io/scinote-api-docs/#introduction).
