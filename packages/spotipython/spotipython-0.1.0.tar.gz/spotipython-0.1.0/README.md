# spotipython

This is a bare bones Spotify Web API client library. It supports async, is typed and is generated directly from an OpenAPI spec.

## Install:

```bash
pip install spotipython
```

## Quickstart


```python
# tests/test_search.py
async def test_take_on_me():
    token = await get_spotify_token(
        client_id="get_this_from_the_dashboard", 
        client_secret="and this too"
    )
    async with AuthenticatedClient(
        base_url="https://api.spotify.com/v1",
        token=token,
        raise_on_unexpected_status=True,
    ) as client:
        while True:
            resp = await search.asyncio_detailed(
                q="Take on Me",
                type_=[SearchTypeItem.TRACK],
                limit=1,
                client=client,
            )

            results = resp.parsed
            assert isinstance(results, SearchResponse200), (
                "results wasn't a SearchResponse200"
            )
            assert isinstance(results.tracks, PagingTrackObject), (
                "tracks wasn't a PagingTrackObject"
            )
            assert isinstance(results.tracks.items, list), "items wasn't a list"
            for t in results.tracks.items:
                assert t.name == "Take on Me", "Track name wasn't 'Take on Me'"
            break
```

Given that it's typed and generated from the [Spotify Web API docs](https://developer.spotify.com/documentation/web-api) (well, sort of, see below) you can work it out from there.

Note that [openapi-python-client uses](https://github.com/openapi-generators/openapi-python-client/discussions/385) `UNSET` rather heavily, which makes things ugly.

## Generic usage guide
_The following was copied from the openapi-python-client's generated README._

_Begin copy-paste:_

<!-- TODO: Change generic examples to specifics. -->

First, create a client:

```python
from generated_client import Client

client = Client(base_url="https://api.example.com")
```

If the endpoints you're going to hit require authentication, use `AuthenticatedClient` instead:

```python
from generated_client import AuthenticatedClient

client = AuthenticatedClient(base_url="https://api.example.com", token="SuperSecretToken")
```

Now call your endpoint and use your models:

```python
from generated_client.models import MyDataModel
from generated_client.api.my_tag import get_my_data_model
from generated_client.types import Response

with client as client:
    my_data: MyDataModel = get_my_data_model.sync(client=client)
    # or if you need more info (e.g. status_code)
    response: Response[MyDataModel] = get_my_data_model.sync_detailed(client=client)
```

Or do the same thing with an async version:

```python
from generated_client.models import MyDataModel
from generated_client.api.my_tag import get_my_data_model
from generated_client.types import Response

async with client as client:
    my_data: MyDataModel = await get_my_data_model.asyncio(client=client)
    response: Response[MyDataModel] = await get_my_data_model.asyncio_detailed(client=client)
```

By default, when you're calling an HTTPS API it will attempt to verify that SSL is working correctly. Using certificate verification is highly recommended most of the time, but sometimes you may need to authenticate to a server (especially an internal server) using a custom certificate bundle.

```python
client = AuthenticatedClient(
    base_url="https://internal_api.example.com", 
    token="SuperSecretToken",
    verify_ssl="/path/to/certificate_bundle.pem",
)
```

You can also disable certificate validation altogether, but beware that **this is a security risk**.

```python
client = AuthenticatedClient(
    base_url="https://internal_api.example.com", 
    token="SuperSecretToken", 
    verify_ssl=False
)
```

Things to know:
1. Every path/method combo becomes a Python module with four functions:
    1. `sync`: Blocking request that returns parsed data (if successful) or `None`
    1. `sync_detailed`: Blocking request that always returns a `Request`, optionally with `parsed` set if the request was successful.
    1. `asyncio`: Like `sync` but async instead of blocking
    1. `asyncio_detailed`: Like `sync_detailed` but async instead of blocking

1. All path/query params, and bodies become method arguments.
1. If your endpoint had any tags on it, the first tag will be used as a module name for the function (my_tag above)
1. Any endpoint which did not have a tag will be in `generated_client.api.default`

### Advanced customisations

There are more settings on the generated `Client` class which let you control more runtime behavior, check out the docstring on that class for more info. You can also customize the underlying `httpx.Client` or `httpx.AsyncClient` (depending on your use-case):

```python
from generated_client import Client

def log_request(request):
    print(f"Request event hook: {request.method} {request.url} - Waiting for response")

def log_response(response):
    request = response.request
    print(f"Response event hook: {request.method} {request.url} - Status {response.status_code}")

client = Client(
    base_url="https://api.example.com",
    httpx_args={"event_hooks": {"request": [log_request], "response": [log_response]}},
)

# Or get the underlying httpx client to modify directly with client.get_httpx_client() or client.get_async_httpx_client()
```

You can even set the httpx client directly, but beware that this will override any existing settings (e.g., base_url):

```python
import httpx
from generated_client import Client

client = Client(
    base_url="https://api.example.com",
)
# Note that base_url needs to be re-set, as would any shared cookies, headers, etc.
client.set_httpx_client(httpx.Client(base_url="https://api.example.com", proxies="http://localhost:8030"))
```


It is generated using [openapi-python-client](https://github.com/openapi-generators/openapi-python-client). That means it benefits from 'all the latest and greatest Python features' such as type annotations, dataclasses and asynchronous execution.

_end copy-paste_

## Development

### Background
I built this because `spotipy`, the most popular Spotify Python SDK, isn't typed, nor does it support async, as far as I can see. None of the other libraries have been updated in the past few months. And in any case, I needed an interface I could trust.

I needed it for [Zacusca](https://zacusca/net), on which [vol.best](https://vol.best) is built. They're both [Banquet](https://bnqt.app) products.

I decided to publish it in case anyone else finds it helpful.

### Generation

To generate the client:

```bash
uv run generator/generator.py
```

This will generate the client in `generated-client/generated_client`. Then it will copy the relevant files across to `spotipython`.

You might notice that in `generator.py` I've hardcoded a non-Spotify URL:

```
https://raw.githubusercontent.com/APIs-guru/openapi-directory/main/APIs/spotify.com/1.0.0/openapi.yaml
```

You can see why [here](https://community.spotify.com/t5/Spotify-for-Developers/OpenApi-Swagger-description-for-the-Web-API/td-p/5196705).

### Testing

I optimistically assume that the Swagger and client generator will work and if they don't then this downstream project is irredeemably broken anyway.

So there's currently only one test. It assumes you have `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` set.

If you encounter problems, tell me.