# Lumos Connector SDK

Plug apps back into Lumos using an integration connector built with this SDK.

[![PyPI - Version](https://img.shields.io/pypi/v/connector-py.svg)](https://pypi.org/project/connector-py)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/connector-py.svg)](https://pypi.org/project/connector-py)

-----

## Table of Contents

- [Lumos Connector SDK](#lumos-connector-sdk)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Print the spec](#print-the-spec)
  - [Create a new connector](#create-a-new-connector)
    - [Learning the connector's capabilities](#learning-the-connectors-capabilities)
    - [Connector implementation](#connector-implementation)
    - [Running unit tests](#running-unit-tests)
    - [Typechecking with MyPy](#typechecking-with-mypy)
    - [Error Handling](#error-handling)
      - [Raising an exception](#raising-an-exception)
      - [Response](#response)
    - [OAuth Module](#oauth-module)
      - [OAuth Flow Types](#oauth-flow-types)
  - [Connector Configuration](#connector-configuration)
    - [Where should I set my connector's configuration?](#where-should-i-set-my-connectors-configuration)
    - [The connection sequence for Lumos](#the-connection-sequence-for-lumos)
  - [Deploying a connector](#deploying-a-connector)
    - [Deployment models](#deployment-models)
  - [Tips](#tips)
    - [The library I want to use is synchronous only](#the-library-i-want-to-use-is-synchronous-only)
  - [License](#license)

## Installation

```console
pip install "connector-py[dev]"
```

## Usage

This package has...

1. A CLI to create a custom connector with its own CLI to call commands
2. A library to assist building custom connectors in Python

To get started with the CLI, run `connector --help`

### Print the spec

This SDK has an OpenAPI spec that you can render and view with the [Swagger editor](https://editor.swagger.io/).

```console
connector spec
```

## Create a new connector

From your shell, run

```shell
# Create a connector
# CLI     cmd      name           folder
connector scaffold demo-connector demo_connector

# Install its dependencies in a virtual env
cd demo_connector
python -m venv .venv
. .venv/bin/activate
pip install ".[all]"

# Lint and run tests
mypy .
pytest

# Run the info capability (note the hyphens, instead of underscores)
demo-connector info
```

### Learning the connector's capabilities

Custom and on-premise Lumos connectors are called via the CLI; they're passed JSON and should print the response JSON to stdout.

Run the `info` capability to learn what other capabilities the connector supports, what resource and entitlement types, its name, etc.

Look at the info, using `jq` to pretty-print the response:

```shell
demo-connector info | jq .response
# or just the capabilities
demo-connector info | jq .response.capabilities
```

To call most capabilities, you run a command where you pass the request (JSON) as a string.

```console
<CONNECTOR COMMAND> <CAPABILITY NAME> --json '<A STRINGIFIED JSON OBJECT>'
```

The most important capability to implement is `validate_credentials`. Lumos uses this capability to ensure a user-established connection works, and has resulted in authentication credentials your connector can use to perform other actions.

```py
test-connector validate_credentials --json '{
    "auth": {
        "oauth": {
            "access_token":"this will not work"
        }
    },
    "request": {},
    "settings": {
        "account_id":"foo"
    }
}'
```

**This is expected to 💥 fail with a brand-new connector**. You'll need to figure out how to [configure the authentication](#connector-configuration) to the underlying app server, and how to surface that as user (auth) configuration.

To learn more about all the capabilities, check out the OpenAPI spec in a Swagger editor.

To see a working capability, you can use the Lumos mock connector's `validate_credentials` call, using `jq` to pretty print the JSON:

```console
mock-connector validate_credentials --json '{"auth":{"basic":{"username":"foo","password":"bar"}},"request":{},"settings":{"host":"google.com"}}' | jq .
```

```json
{
  "response": {
    "valid": true,
    "unique_tenant_id": "mock-connector-tenant-id"
  },
  "page": null
}
```

### Connector implementation

Connectors can implement whichever Lumos capabilities make sense for the underlying app.

To see what a minimal implementation looks like, you can inspect a newly scaffolded connector, and look at the integration declaration, and the _uncommented out_ capability registrations.

The integration declaration looks something like this:

```python
integration = Integration(
    app_id="my_app",
    version=__version__,
    auth=BasicCredential,
    settings_model=MyAppSettings,
    exception_handlers=[
        (httpx.HTTPStatusError, HTTPHandler, None),
    ],
    description_data=DescriptionData(
        logo_url="https://logo.clearbit.com/foobar.com",
        user_friendly_name="Foo Bar",
        description="Foobar is a cloud-based platform that lets you manage foos and bars",
        categories=[AppCategory.DEVELOPERS, AppCategory.COLLABORATION],
    ),
    resource_types=resource_types,
    entitlement_types=entitlement_types,
)
```

And capability registration looks something like this:

```py
@integration.register_capability(StandardCapabilityName.LIST_ACCOUNTS)
async def list_accounts(request: ListAccountsRequest) -> ListAccountsResponse:
    # do whatever is needed to get accounts, probably make an http call
    return ListAccountsResponse(
        response=[],
        ...
    )
```

### Running unit tests

Scaffolded connectors come with a bunch of unit test examples - they're all skipped by default, but you can remove the skip marker to use the existing test.

To run unit tests:

```console
pytest .
```

To understand the test structure:

```text
demo_connector/
    demo_connector/
    tests/
        test_basic_capabilities/
            test_list_accounts_cases.py
            test_list_accounts.py
            ...
```

- `test_list_accounts.py` is the actual Pytest test code. It uses all the existing test cases from
- `test_list_accounts_cases.py`

You can see the reference here

```py
@pytest_cases.parametrize_with_cases(
    ["args", "response_body_map", "expected_response"],
    cases=[
        # The name of the Python module
        "tests.test_basic_capabilities.test_list_accounts_cases",
    ],
)
```

### Typechecking with MyPy

The generated Python code is typed, and can be typechecked with MyPy (installed as a dev dependency).

```console
mypy .
```

### Error Handling

Error handling is facilitated through an exception handler decorator.

An exception handler can be attached to the connector library as follows:

```python
from httpx import HTTPStatusError
from connector.oai.errors import HTTPHandler

integration = Integration(
    ...,
    exception_handlers=[
        (HTTPStatusError, HTTPHandler, None),
    ],
    handle_errors=True,
)
```

The decorator accepts a list of tuples of three.

1. the exception type you would like to catch
2. the handler (default or implemented on your own)
3. a specific error code that you would like to associate with this handler.

By default it is recommended to make use of the default HTTPHandler which will handle `raise_for_status()` for you and properly error code it. For more complex errors it is recommended to subclass the ExceptionHandler (in `connector/oai/errors.py`) and craft your own handler.

#### Raising an exception

Among this, there is a custom exception class available as well as a default list of error codes:

```python
from connector.oai.errors import ConnectorError
from connector_sdk_types.generated import ErrorCode

def some_method(self, args):
    raise ConnectorError(
        message="Received wrong data, x: y",
        app_error_code="foobar.some_unique_string",
        error_code=ErrorCode.BAD_REQUEST,
    )
```

It is preferred to raise any manually raisable exception with this class. A connector can implement its own error codes list, which should be properly documented.

#### Response

An example response when handled this way:

```json
// BAD_REQUEST error from github connector
{"error":{"message":"Some message","status_code":400,"error_code":"bad_request","raised_by":"HTTPStatusError","raised_in":"github.integration:validate_credentials"}, "response": null, "raw_data": null}
```

### OAuth Module

The OAuth module is responsible for handling the OAuth2.0 flow for a connector.
It is configured with `oauth_settings` in the `Integration` class.
Not configuring this object will disable the OAuth module completely.

```python
from connector.oai.modules.oauth_module_types import (
    OAuthSettings,
    OAuthCapabilities,
    OAuthRequest,
    RequestDataType,
)

integration = Integration(
    ...,
    oauth_settings=OAuthSettings(
        # Authorization & Token URLs for the particular connector
        authorization_url="https://app.connector.com/oauth/authorize",
        token_url="https://api.connector.com/oauth/v1/token",

        # Scopes per capability (space delimited string)
        scopes={
            StandardCapabilityName.VALIDATE_CREDENTIALS: "test:scope another:scope",
            ... # further capabilities as implemented in the connector
        },

        # You can modify the request type if the default is not appropriate
        # common options for method are "POST" and "GET"
        # available options for data are "FORMDATA", "QUERY", and "JSON" (form-data / url query params / json body)
        # *default is POST and FORMDATA*
        request_type=OAuthRequest(data=RequestDataType.FORMDATA),

        # You can modify the authentication method if the default is not appropriate
        # available options for auth_method are "CLIENT_SECRET_POST" and "CLIENT_SECRET_BASIC"
        # *default is CLIENT_SECRET_POST*
        client_auth=ClientAuthenticationMethod.CLIENT_SECRET_POST,

        # You can turn off specific or all capabilities for the OAuth module
        # This means that these will either be skipped or you have to implement them manually
        capabilities=OAuthCapabilities(
            refresh_access_token=False,
        ),

        # You can specify the type of OAuth flow to use
        # Available options are "CODE_FLOW" and "CLIENT_CREDENTIALS"
        # *default is CODE_FLOW*
        flow_type=OAuthFlowType.CODE_FLOW,

        # You can enable PKCE (Proof Key for Code Exchange)
        # *default is False*
        # S256 is the default hashing algorithm, and the only supported at the moment
        pkce=True,
    ),
)
```

It might happen that your integration requires a dynamic authorization/token URL.
For example when the service provider has specific URLs and uses the customers custom subdomain. (eg. `https://{subdomain}.service.com/oauth/authorize`)
In that case you can pass a callable that takes the request args (`AuthRequest`, without the auth parameter) as an argument (only available during request).

```python
# method definitions
def get_authorization_url(args: AuthRequest) -> str:
    settings = get_settings(args, ConnectorSettings)
    return f"https://{settings.subdomain}.service.com/oauth/authorize"

def get_token_url(args: AuthRequest) -> str:
    settings = get_settings(args, ConnectorSettings)
    return f"https://{settings.subdomain}.service.com/oauth/token"

# oauth settings
integration = Integration(
    ...,
    oauth_settings=OAuthSettings(
        authorization_url=get_authorization_url,
        token_url=get_token_url,
    ),
)
```

#### OAuth Flow Types

The OAuth module supports two flow types:

- `CODE_FLOW`: The authorization code flow (default)
- `CLIENT_CREDENTIALS`: The client credentials flow (sometimes called "2-legged OAuth" or "Machine-to-Machine OAuth")

The flow type can be specified in the `OAuthSettings` object.

Using the authorization code flow you have three available capabilities:

- `GET_AUTHORIZATION_URL`: To get the authorization URL
- `HANDLE_AUTHORIZATION_CALLBACK`: To handle the authorization callback
- `REFRESH_ACCESS_TOKEN`: To refresh the access token

Using the client credentials flow you have two available capabilities:

- `HANDLE_CLIENT_CREDENTIALS_REQUEST`: To handle the client credentials request, uses the token URL
- `REFRESH_ACCESS_TOKEN`: To refresh the access token

These are registered by default via the module and can be overriden by the connector.

If you run:

```sh
connector info
```

You will see that the OAuth capabilities are included in the available connector capabilities.

## Connector Configuration

A connector is used to connect to multiple tenants of the same app. Each tenant has a connection in Lumos, and the unique tenant ID is used to distinguish the different connections.

Each connection has its own...

- ...auth object that fits the connector's auth model.
- ...settings object that fits the connector's settings model.
- ...set of data (accounts, resources, entitlements) that Lumos reads and stores.

![How a connector is used](https://lumos-static.s3.us-west-2.amazonaws.com/prod/public/sdk-documentation/connector-tenant-data-model.png)

A connector can be used for multiple underlying instances of the same app. For instance, you might use a `github` connector to establish connections with different Github Organizations. The nature of "what is a tenant" is dependent on the underlying app.

A scaffolded connector has OAuth authentication, and a Settings type with `account_id`. You don't have to keep these - you can change the authentication model and the Settings type to whatever is appropriate for the underlying app (settings may be empty).

### Where should I set my connector's configuration?

A quick rule is sensitive data that would allow an attacker the ability to access the underlying app, goes into the `auth` payload. Anything else that's not sensitive, not absolutely required to connect to a tenant, or can have a sane default, is `settings`.

### The connection sequence for Lumos

1. Lumos sees a new connector, and queries its settings and auth models via the `info` command.
2. Lumos uses these parts of the `info` response to render a connection form for the user.
    - the settings (JSON schema + included documentation)
    - auth models (string matching to the auth model)
    - app logo, description, tags, etc.
3. The user enters all the relevant data/auth materials to connect to an app, and/or does an OAuth consent flow to the underlying app.
4. Lumos validates the credentials and settings via the `validate_credentials` capability.

![The process of connecting a new connector](https://lumos-static.s3.us-west-2.amazonaws.com/prod/public/sdk-documentation/connector-setup.png)

At this point, the connection is considered established, and Lumos will attempt to read all data from the connector, allow user provisioning and deprovisioning, etc.

## Deploying a connector

Quick steps:

1. Package up the connector you've built into an archive with a native executable. We use [`pyinstaller`](https://pyinstaller.org/en/stable/) for our Python connectors.

    ```shell
    # SDK     command         ...required args
    connector compile-on-prem --connector-root-module-dir ./demo_connector/demo_connector --app-id demo
    ```

2. Run the [Lumos on-premise agent](https://developers.lumos.com/reference/on-premise-agent).
3. On the same machine as (3), deploy the packaged-up connector from (1) in the same folder.
4. The integration should show up in the Lumos AdminView > Integrations screen.

### Deployment models

Lumos calls a connector's APIs with auth and settings data to read all the accounts, entitlements, resources, and associations in the connected app.

There are two ways this happens, depending on who's hosting the connector.

If Lumos is hosting it, we call it directly in our backend.

![Lumos hosts and calls our own connectors](https://lumos-static.s3.us-west-2.amazonaws.com/prod/public/sdk-documentation/connector-hosting-lumos.png)

If it's a custom connector, it runs as an on-premise connector on a customer's computer, and is called by the [Lumos on-prem agent](https://developers.lumos.com/reference/on-premise-agent).

![Lumos hosts and calls our own connectors](https://lumos-static.s3.us-west-2.amazonaws.com/prod/public/sdk-documentation/connector-hosting-onprem.png)

## Tips

### The library I want to use is synchronous only

You can use a package called `asgiref`. This package converts I/O bound synchronous
calls into asyncio non-blocking calls. First, add asgiref to your dependencies list
in `pyproject.toml`. Then, in your async code, use `asgiref.sync_to_async` to convert
synchronous calls to asynchronous calls.

```python
from asgiref.sync import sync_to_async
import requests

async def async_get_data():
    response = await sync_to_async(requests.get)("url")
```

## License

`connector` is distributed under the terms of the [Apache 2.0](./LICENSE.txt) license.
