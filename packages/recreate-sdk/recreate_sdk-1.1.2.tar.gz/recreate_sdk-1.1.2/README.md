# Recreate SDK Python API library

<!-- prettier-ignore -->
[![PyPI version](https://img.shields.io/pypi/v/recreate_sdk.svg?label=pypi%20(stable))](https://pypi.org/project/recreate_sdk/)

The ProSights Recreate SDK Python library provides convenient access to the Recreate SDK REST API from any Python 3.8+
application. The library includes type definitions for all request params and response fields,
and offers both synchronous and asynchronous clients powered by [httpx](https://github.com/encode/httpx).

It is generated with [Stainless](https://www.stainless.com/).

## Documentation

The full API of this library can be found in [api.md](api.md).

## Installation

```sh
# install from PyPI
pip install recreate_sdk
```

## Usage

The full API of this library can be found in [api.md](api.md).
We require an RECREATE_API_KEY and a RECREATE_BASE_URL to be set to function appropriately.
If you need access to either an API_KEY or need to know your BASE_URL, please reach out to support@prosights.co

```python
import os
from recreate_sdk import RecreateSDK

client = RecreateSDK(
    api_key=os.getenv("RECREATE_API_KEY"), base_url=os.getenv("RECREATE_BASE_URL")
)

def main():
    with open("test-pdf.pdf", "rb") as file:
        response = client.enterprise_api.recreate.create(
            file=file,
            selected_pages="1-5",
            is_ppt_process_enabled="true",
            is_xls_process_charts_enabled="true",
            is_xls_process_tables_enabled="true",
        )
        print(response)

        response = client.enterprise_api.recreate.retrieve_status(
            recreate_id=response.data.get("recreate_id")
        )
        print(response)

```

This will print out something like 
```
EnterpriseAPIResponse(status='SUCCESS', data={'recreate_id': 'cf9b1754-8dd6-4ef1-a3b4-9615411f1363', 'status': 'CREATED'})
EnterpriseAPIResponse(status='SUCCESS', data={'recreate_id': 'cf9b1754-8dd6-4ef1-a3b4-9615411f1363', 'status': 'RECEIVED', 'xls_download_url': None, 'ppt_download_url': None, 'jobs': [{'job_id': 'e2e7df57-c11b-44ab-8d6b-7d21e9e52c61', 'job_type': 'PPT_PROCESS_PDF_JOB', 'page_number': -1, 'num_cells': None, 'status': 'CREATED'}, {'job_id': 'e38629e5-6138-43bd-a55a-39829aef4e2d', 'job_type': 'XLS_PROCESS_TABLES_JOB', 'page_number': 1, 'num_cells': None, 'status': 'CREATED'}, {'job_id': '082a347c-67b9-4610-b746-03f4e7771451', 'job_type': 'XLS_PROCESS_CHARTS_JOB', 'page_number': 1, 'num_cells': None, 'status': 'CREATED'}]})
```

## Async usage

Simply import `AsyncRecreateSDK` instead of `RecreateSDK` and use `await` with each API call:

```python
import os
import asyncio
from recreate_sdk import AsyncRecreateSDK

client = AsyncRecreateSDK(
    api_key=os.environ.get("RECREATE_SDK_API_KEY"),  # This is the default and can be omitted
)


async def main() -> None:
    response = await client.enterprise_api.validate_token(
        token="token",
    )
    print(response.valid)


asyncio.run(main())
```

Functionality between the synchronous and asynchronous clients is otherwise identical.

### With aiohttp

By default, the async client uses `httpx` for HTTP requests. However, for improved concurrency performance you may also use `aiohttp` as the HTTP backend.

You can enable this by installing `aiohttp`:

```sh
# install from PyPI
pip install recreate_sdk[aiohttp]
```

Then you can enable it by instantiating the client with `http_client=DefaultAioHttpClient()`:

```python
import asyncio
from recreate_sdk import DefaultAioHttpClient
from recreate_sdk import AsyncRecreateSDK


async def main() -> None:
    async with AsyncRecreateSDK(
        api_key="My API Key",
        http_client=DefaultAioHttpClient(),
    ) as client:
        response = await client.enterprise_api.validate_token(
            token="token",
        )
        print(response.valid)


asyncio.run(main())
```

## Using types

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods for things like:

- Serializing back into JSON, `model.to_json()`
- Converting to a dictionary, `model.to_dict()`

Typed requests and responses provide autocomplete and documentation within your editor. If you would like to see type errors in VS Code to help catch bugs earlier, set `python.analysis.typeCheckingMode` to `basic`.

## File uploads

Request parameters that correspond to file uploads can be passed as `bytes`, or a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance or a tuple of `(filename, contents, media type)`.

```python
from pathlib import Path
from recreate_sdk import RecreateSDK

client = RecreateSDK()

client.enterprise_api.unprotect_pdf(
    file=Path("/path/to/file"),
    password="password",
)
```

The async client uses the exact same interface. If you pass a [`PathLike`](https://docs.python.org/3/library/os.html#os.PathLike) instance, the file contents will be read asynchronously automatically.

## Handling errors

When the library is unable to connect to the API (for example, due to network connection problems or a timeout), a subclass of `recreate_sdk.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx
response), a subclass of `recreate_sdk.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `recreate_sdk.APIError`.

```python
import recreate_sdk
from recreate_sdk import RecreateSDK

client = RecreateSDK()

try:
    client.enterprise_api.validate_token(
        token="token",
    )
except recreate_sdk.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except recreate_sdk.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except recreate_sdk.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

Error codes are as follows:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

### Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff.
Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict,
429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable retry settings:

```python
from recreate_sdk import RecreateSDK

# Configure the default for all requests:
client = RecreateSDK(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
client.with_options(max_retries=5).enterprise_api.validate_token(
    token="token",
)
```

### Timeouts

By default requests time out after 1 minute. You can configure this with a `timeout` option,
which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/timeouts/#fine-tuning-the-configuration) object:

```python
from recreate_sdk import RecreateSDK

# Configure the default for all requests:
client = RecreateSDK(
    # 20 seconds (default is 1 minute)
    timeout=20.0,
)

# More granular control:
client = RecreateSDK(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
client.with_options(timeout=5.0).enterprise_api.validate_token(
    token="token",
)
```

On timeout, an `APITimeoutError` is thrown.

Note that requests that time out are [retried twice by default](#retries).

## Advanced

### Logging

We use the standard library [`logging`](https://docs.python.org/3/library/logging.html) module.

You can enable logging by setting the environment variable `RECREATE_SDK_LOG` to `info`.

```shell
$ export RECREATE_SDK_LOG=info
```

Or to `debug` for more verbose logging.

### How to tell whether `None` means `null` or missing

In an API response, a field may be explicitly `null`, or missing entirely; in either case, its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:

```py
if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
```

### Accessing raw response data (e.g. headers)

The "raw" Response object can be accessed by prefixing `.with_raw_response.` to any HTTP method call, e.g.,

```py
from recreate_sdk import RecreateSDK

client = RecreateSDK()
response = client.enterprise_api.with_raw_response.validate_token(
    token="token",
)
print(response.headers.get('X-My-Header'))

enterprise_api = response.parse()  # get the object that `enterprise_api.validate_token()` would have returned
print(enterprise_api.valid)
```

These methods return an [`APIResponse`](https://github.com/prosights/recreate-sdk-python/tree/main/src/recreate_sdk/_response.py) object.

The async client returns an [`AsyncAPIResponse`](https://github.com/prosights/recreate-sdk-python/tree/main/src/recreate_sdk/_response.py) with the same structure, the only difference being `await`able methods for reading the response content.

#### `.with_streaming_response`

The above interface eagerly reads the full response body when you make the request, which may not always be what you want.

To stream the response body, use `.with_streaming_response` instead, which requires a context manager and only reads the response body once you call `.read()`, `.text()`, `.json()`, `.iter_bytes()`, `.iter_text()`, `.iter_lines()` or `.parse()`. In the async client, these are async methods.

```python
with client.enterprise_api.with_streaming_response.validate_token(
    token="token",
) as response:
    print(response.headers.get("X-My-Header"))

    for line in response.iter_lines():
        print(line)
```

The context manager is required so that the response will reliably be closed.

### Making custom/undocumented requests

This library is typed for convenient access to the documented API.

If you need to access undocumented endpoints, params, or response properties, the library can still be used.

#### Undocumented endpoints

To make requests to undocumented endpoints, you can make requests using `client.get`, `client.post`, and other
http verbs. Options on the client will be respected (such as retries) when making this request.

```py
import httpx

response = client.post(
    "/foo",
    cast_to=httpx.Response,
    body={"my_param": True},
)

print(response.headers.get("x-foo"))
```

#### Undocumented request params

If you want to explicitly send an extra param, you can do so with the `extra_query`, `extra_body`, and `extra_headers` request
options.

#### Undocumented response properties

To access undocumented response properties, you can access the extra fields like `response.unknown_prop`. You
can also get all the extra fields on the Pydantic model as a dict with
[`response.model_extra`](https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_extra).

### Configuring the HTTP client

You can directly override the [httpx client](https://www.python-httpx.org/api/#client) to customize it for your use case, including:

- Support for [proxies](https://www.python-httpx.org/advanced/proxies/)
- Custom [transports](https://www.python-httpx.org/advanced/transports/)
- Additional [advanced](https://www.python-httpx.org/advanced/clients/) functionality

```python
import httpx
from recreate_sdk import RecreateSDK, DefaultHttpxClient

client = RecreateSDK(
    # Or use the `RECREATE_SDK_BASE_URL` env var
    base_url="http://my.test.server.example.com:8083",
    http_client=DefaultHttpxClient(
        proxy="http://my.test.proxy.example.com",
        transport=httpx.HTTPTransport(local_address="0.0.0.0"),
    ),
)
```

You can also customize the client on a per-request basis by using `with_options()`:

```python
client.with_options(http_client=DefaultHttpxClient(...))
```

### Managing HTTP resources

By default the library closes underlying HTTP connections whenever the client is [garbage collected](https://docs.python.org/3/reference/datamodel.html#object.__del__). You can manually close the client using the `.close()` method if desired, or with a context manager that closes when exiting.

```py
from recreate_sdk import RecreateSDK

with RecreateSDK() as client:
  # make requests here
  ...

# HTTP client is now closed
```

## Versioning

This package generally follows [SemVer](https://semver.org/spec/v2.0.0.html) conventions, though certain backwards-incompatible changes may be released as minor versions:

1. Changes that only affect static types, without breaking runtime behavior.
2. Changes to library internals which are technically public but not intended or documented for external use. _(Please open a GitHub issue to let us know if you are relying on such internals.)_
3. Changes that we do not expect to impact the vast majority of users in practice.

We take backwards-compatibility seriously and work hard to ensure you can rely on a smooth upgrade experience.

We are keen for your feedback; please open an [issue](https://www.github.com/prosights/recreate-sdk-python/issues) with questions, bugs, or suggestions.

### Determining the installed version

If you've upgraded to the latest version but aren't seeing any new features you were expecting then your python environment is likely still using an older version.

You can determine the version that is being used at runtime with:

```py
import recreate_sdk
print(recreate_sdk.__version__)
```

## Requirements

Python 3.8 or higher.

## Contributing

See [the contributing documentation](./CONTRIBUTING.md).
