# EnterpriseAPI

Types:

```python
from recreate_sdk.types import EnterpriseAPIValidateTokenResponse
```

Methods:

- <code title="get /enterprise-api/formats/">client.enterprise_api.<a href="./src/recreate_sdk/resources/enterprise_api/enterprise_api.py">list_formats</a>() -> <a href="./src/recreate_sdk/types/enterprise_api/enterprise_api_response.py">EnterpriseAPIResponse</a></code>
- <code title="post /enterprise-api/unprotect-pdf/">client.enterprise_api.<a href="./src/recreate_sdk/resources/enterprise_api/enterprise_api.py">unprotect_pdf</a>(\*\*<a href="src/recreate_sdk/types/enterprise_api_unprotect_pdf_params.py">params</a>) -> object</code>
- <code title="post /enterprise-api/validate-token">client.enterprise_api.<a href="./src/recreate_sdk/resources/enterprise_api/enterprise_api.py">validate_token</a>(\*\*<a href="src/recreate_sdk/types/enterprise_api_validate_token_params.py">params</a>) -> <a href="./src/recreate_sdk/types/enterprise_api_validate_token_response.py">EnterpriseAPIValidateTokenResponse</a></code>

## Recreate

Types:

```python
from recreate_sdk.types.enterprise_api import EnterpriseAPIResponse, RecreateGetJsonResponse
```

Methods:

- <code title="post /enterprise-api/recreate/">client.enterprise_api.recreate.<a href="./src/recreate_sdk/resources/enterprise_api/recreate.py">create</a>(\*\*<a href="src/recreate_sdk/types/enterprise_api/recreate_create_params.py">params</a>) -> <a href="./src/recreate_sdk/types/enterprise_api/enterprise_api_response.py">EnterpriseAPIResponse</a></code>
- <code title="get /enterprise-api/recreate/{recreate_id}/to_json">client.enterprise_api.recreate.<a href="./src/recreate_sdk/resources/enterprise_api/recreate.py">get_json</a>(recreate_id) -> <a href="./src/recreate_sdk/types/enterprise_api/recreate_get_json_response.py">RecreateGetJsonResponse</a></code>
- <code title="post /enterprise-api/recreate/hide/">client.enterprise_api.recreate.<a href="./src/recreate_sdk/resources/enterprise_api/recreate.py">hide</a>() -> <a href="./src/recreate_sdk/types/enterprise_api/enterprise_api_response.py">EnterpriseAPIResponse</a></code>
- <code title="get /enterprise-api/recreate/status/">client.enterprise_api.recreate.<a href="./src/recreate_sdk/resources/enterprise_api/recreate.py">retrieve_status</a>(\*\*<a href="src/recreate_sdk/types/enterprise_api/recreate_retrieve_status_params.py">params</a>) -> <a href="./src/recreate_sdk/types/enterprise_api/enterprise_api_response.py">EnterpriseAPIResponse</a></code>
