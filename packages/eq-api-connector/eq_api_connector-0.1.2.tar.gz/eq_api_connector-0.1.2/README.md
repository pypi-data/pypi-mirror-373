# eq-api-connector
A small python package to handle authentication and act as a generic api sdk.

It supports apis Public client applications using [acquire_token_interactive](https://learn.microsoft.com/en-us/python/api/msal/msal.application.publicclientapplication?view=msal-py-latest#msal-application-publicclientapplication-acquire-token-interactive) and contains a few basic endpoint accessors. 

# Install
Install from pypi ```pip install eq-api-connector``` or clone and use ```poetry install``` as a developer.

# Usage
See the dummy example below

```
from eq_api_connector import set_url_prod, set_scope, set_public_client_id, get_json

url_prod = "https://api.gateway.equinor.com/dummy/v1"
client_id = "insert_your_client_id_here"  # IOC SME monitoring SDK
scope = ["34de7368-10f7-4c34-a4df-928156065f2c/ReadWrite"]

set_url_prod(url_prod)
set_scope(scope)
set_public_client_id(client_id)

model_owners = get_json("/example-endpoint")
````


