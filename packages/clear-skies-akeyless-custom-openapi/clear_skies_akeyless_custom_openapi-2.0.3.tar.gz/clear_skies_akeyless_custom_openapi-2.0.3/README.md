# openapi

OpenApi dynamic producer for Akeyless

## Installation

```
pip install clear-skies-akeyless-custom-openapi
```

## Producer Payload

The payload for this producer looks like:

```
{"api_key": "ADMIN_API_KEY_HERE", "id": "ID_FOR_THE_ADMIN_API_KEY"}
```

You do need the id for your API key, as this is later required when revoking a key.  Unfortunately, the OpenAPI UI does not provide this, and the endpoints used from the admin api key dashboard also don't return the id of the API key.  Therefore, some extra effort is required to fetch it.  You have to use your new API key in order to list the admin API keys in your account and find the id of your key that way.  The following command typically works:

```
export OPENAI_ADMIN_KEY='YOUR_NEW_KEY_HERE'
curl https://api.openai.com/v1/organization/admin_api_keys \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
```

Which will return something like:

```
{
  "object": "list",
  "data": [
    {
      "object": "organization.admin_api_key",
      "id": "key_abc",
      "name": "Main Admin Key",
      "redacted_value": "sk-admin...def",
      "created_at": 1711471533,
      "last_used_at": 1711471534,
      "owner": {
        "type": "service_account",
        "object": "organization.service_account",
        "id": "sa_456",
        "name": "My Service Account",
        "created_at": 1711471533,
        "role": "member"
      }
    }
  ],
  "first_id": "key_abc",
  "last_id": "key_abc",
  "has_more": false
}
```

You want the `.data.id` parameter.  Note that if you have multiple keys, you must make sure you find the one you just created (based on the name).  If you already have a number of keys for your account, you may have to paginate through the results to find the newly created id.

## Producer Setup

Call `clearskies_akeyless_custom_openapi.build_openapi_producer()` to initialize the create/revoke endpoints.  You can
optionally provide the `url` parameter which will add a prefix to the endpoints.  This can then be attached to a
[clearskies context](https://clearskies.info/docs/context/index.html) or an [endpoint group](https://clearskies.info/docs/endpoint-groups/endpoint-groups.html):

If used as a producer, it will use the provided credentials to fetch and return a temporary OpenApi admin key.  It can also be used as a rotator,
in which case it will generate a new admin key and revoke the old one.

## Usage Example

```python
import clearskies
import clearskies_akeyless_custom_openapi

wsgi = clearskies.contexts.WsgiRef(
    clearskies_akeyless_custom_openapi.build_openapi_producer()
)
wsgi()
```

Which you can test directly using calls like:

```
curl 'http://localhost:8080/sync/create' -d '{"payload":"{\"api_key\":\"YOUR_ADMIN_API_KEY_HERE\",\"id\":\"ID_OF_ADMIN_API_KEY_HERE\"}"}'

curl 'http://localhost:8080/sync/revoke' -d '{"payload":"{\"api_key\":\"YOUR_ADMIN_API_KEY_HERE\",\"id\":\"ID_OF_ADMIN_API_KEY_HERE\"}"}'
```

Or if hosting multiple custom producers from one server:

```python
import clearskies
import clearskies_akeyless_custom_openapi

wsgi = clearskies.contexts.WsgiRef(
    clearskies.EndpointGroup(
        clearskies_akeyless_custom_openapi.build_openapi_producer(url='openapi')
    ),
)
wsgi()
```

Which you can test directly using calls like:

```
curl 'http://localhost:8080/openapi/sync/create' -d '{"payload":"{\"api_key\":\"YOUR_ADMIN_API_KEY_HERE\",\"id\":\"ID_OF_ADMIN_API_KEY_HERE\"}"}'

curl 'http://localhost:8080/openapi/sync/revoke' -d '{"payload":"{\"api_key\":\"YOUR_ADMIN_API_KEY_HERE\",\"id\":\"ID_OF_ADMIN_API_KEY_HERE\"}"}'
```

**NOTE:** The WsgiRef context is not intended for production use, so you'll want to switch that out for [another context](https://clearskies.info/docs/context/index.html) more appropriate for your setup.

**NOTE:** Akeyless doesn't store your payload as JSON, even when you put in a JSON payload.  Instead, it ends up as a stringified-json
(hence the escaped apostrophes in the above example commands).  This is normal, and normally invisible to you, unless you try to invoke the
endpoints yourself.

## Development

To set up your development environment with pre-commit hooks:

```bash
# Install uv if not already installed
pip install uv

# Create a virtual environment and install all dependencies (including dev)
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Optionally, run pre-commit on all files
uv run pre-commit run --all-files
```
