# {title} Connector

[![PyPI - Version](https://img.shields.io/pypi/v/connector-{hyphenated_name}.svg)](https://pypi.org/project/connector-{hyphenated_name})
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/connector-{hyphenated_name}.svg)](https://pypi.org/project/connector-{hyphenated_name})

-----

## Table of Contents

- [Capabilities](#capabilities)
- [Installation](#installation)
- [Authentication](#authentication)
- [Settings](#settings)
- [Usage](#usage)
- [License](#license)


## Capabilities
List of implemented capabilities:

[//]: # (- **validate_credentials**)

[//]: # (- **list_accounts**)

[//]: # (- **list_resources**)

[//]: # (- **list_entitlements**)

[//]: # (- **find_entitlement_associations**)

[//]: # (- **get_last_activity**)

[//]: # (- **assign_entitlement**)

[//]: # (- **unassign_entitlement**)

[//]: # (- **create_account**)

[//]: # (- **activate_account**)

[//]: # (- **deactivate_account**)

[//]: # (- **delete_account**)

## Installation

If this connector is in the Lumos monorepo, ensure `connector-{hyphenated_name}` is added
to the top level `pyproject.toml` file. Otherwise:

```console
pip install connector-{hyphenated_name}[dev,fastapi]
```

If you want the HTTP server, `pip install connector-{hyphenated_name}[fastapi]`

If you're on Mac, you'll need to escape the square brackets in your ZSH shell:

```console
pip install connector-{hyphenated_name}\[dev,fastapi\]
```


## Authentication

Here you should describe how to authenticate with the service. For example, if the service uses API keys, you should provide instructions on how to generate and use them.

## Settings

Here you should describe the settings that the connector uses. For example, if the service requires a specific domain to be set, you should provide instructions on how to set it.
This includes information like:

- What type of settings go into the connector setting
- Where can we acquire these parameters
- Any caveats or abnormalities regarding the setting parameters


## Usage

The package can be used in three ways:
1. A CLI to scaffold a custom connector with its own CLI to call commands
2. A library to create custom connector
3. A library to convert your custom connector code to a FastAPI HTTP server

To get started, run `{hyphenated_name} --help`

An example of running a command that accepts arguments:

```shell
{hyphenated_name} info --json '{{"a": 1}}'
```

### Hacking

There are some positional arguments under the "hacking" command for ease of development.

```console
{hyphenated_name} hacking --help
```

For instance, you can spin up a FastAPI server with the following command:

```console
{hyphenated_name} hacking http-server
```

If you navigate to http://localhost:8000/docs, you'll be able to run a Swagger UI to test your
endpoints.

## License

`connector-{hyphenated_name}` is distributed under the terms of the [Apache 2.0](./LICENSE.txt) license.


