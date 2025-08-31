# agilicus_api.PermissionsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_delete_resource_permission**](PermissionsApi.md#bulk_delete_resource_permission) | **DELETE** /v1/resource_permissions | Delete a set of resource permissions matching the resource id
[**create_resource_permission**](PermissionsApi.md#create_resource_permission) | **POST** /v1/resource_permissions | Create a ResourcePermission
[**create_resource_role**](PermissionsApi.md#create_resource_role) | **POST** /v1/resources/{resource_type}/roles | Create a ResourceRole
[**delete_resource_permission**](PermissionsApi.md#delete_resource_permission) | **DELETE** /v1/resource_permissions/{resource_permission_id} | Delete a ResourcePermission
[**delete_resource_role**](PermissionsApi.md#delete_resource_role) | **DELETE** /v1/resources/{resource_type}/roles/{role_name} | Delete a ResourceRole
[**get_elevated_user_roles**](PermissionsApi.md#get_elevated_user_roles) | **GET** /v1/elevated_permissions/{user_id} | Get elevated roles for a user
[**get_resource_permission**](PermissionsApi.md#get_resource_permission) | **GET** /v1/resource_permissions/{resource_permission_id} | Get a ResourcePermission
[**get_resource_role**](PermissionsApi.md#get_resource_role) | **GET** /v1/resources/{resource_type}/roles/{role_name} | Get a ResourceRole
[**list_elevated_user_roles**](PermissionsApi.md#list_elevated_user_roles) | **GET** /v1/elevated_permissions | List all elevated users and their roles
[**list_resource_permissions**](PermissionsApi.md#list_resource_permissions) | **GET** /v1/resource_permissions | List all ResourcePermissions
[**list_resource_roles**](PermissionsApi.md#list_resource_roles) | **GET** /v1/resource_roles | List all ResourceRoles
[**list_resource_roles_for_type**](PermissionsApi.md#list_resource_roles_for_type) | **GET** /v1/resources/{resource_type}/roles | List all ResourceRoles
[**replace_elevated_user_role**](PermissionsApi.md#replace_elevated_user_role) | **PUT** /v1/elevated_permissions/{user_id} | Create or update an elevated user role
[**replace_resource_permission**](PermissionsApi.md#replace_resource_permission) | **PUT** /v1/resource_permissions/{resource_permission_id} | Update a ResourcePermission
[**replace_resource_role**](PermissionsApi.md#replace_resource_role) | **PUT** /v1/resources/{resource_type}/roles/{role_name} | Update a ResourceRole


# **bulk_delete_resource_permission**
> bulk_delete_resource_permission()

Delete a set of resource permissions matching the resource id

Delete a set of resource permissions matching the resource

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.resource_type_enum import ResourceTypeEnum
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    resource_id = "owner" # str | The id of the resource to query for (optional)
    resource_type = ResourceTypeEnum("fileshare") # ResourceTypeEnum | The type of resource to query for (optional)
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a set of resource permissions matching the resource id
        api_instance.bulk_delete_resource_permission(org_id=org_id, resource_id=resource_id, resource_type=resource_type, user_id=user_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->bulk_delete_resource_permission: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **resource_id** | **str**| The id of the resource to query for | [optional]
 **resource_type** | **ResourceTypeEnum**| The type of resource to query for | [optional]
 **user_id** | **str**| Query based on user id | [optional]

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | ResourcePermission deleted |  -  |
**404** | ResourcePermission not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_resource_permission**
> ResourcePermission create_resource_permission(resource_permission)

Create a ResourcePermission

Create a ResourcePermission

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.resource_permission import ResourcePermission
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    resource_permission = ResourcePermission(
        metadata=MetadataWithId(),
        spec=ResourcePermissionSpec(
            user_id="549sSkfdsksakSKD40",
            org_id="IAsl3dl40aSsfLKiU76",
            resource_id="s9df932aSFl48sazZ4",
            resource_type="fileshare",
            resource_role_name="fileshare",
        ),
    ) # ResourcePermission | 

    # example passing only required values which don't have defaults set
    try:
        # Create a ResourcePermission
        api_response = api_instance.create_resource_permission(resource_permission)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->create_resource_permission: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_permission** | [**ResourcePermission**](ResourcePermission.md)|  |

### Return type

[**ResourcePermission**](ResourcePermission.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New ResourcePermission created |  -  |
**409** | An ResourcePermission with the same name already exists for this resource_type. The existing ResourcePermission is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_resource_role**
> ResourceRole create_resource_role(resource_type, resource_role)

Create a ResourceRole

Create a ResourceRole

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.resource_role import ResourceRole
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    resource_type = "fileshare" # str | The type of resource in the path
    resource_role = ResourceRole(
        metadata=MetadataWithId(),
        spec=ResourceRoleSpec(
            resource_type="fileshare",
            role_name="owner",
            description="Provides full access to the the file share.",
        ),
    ) # ResourceRole | 

    # example passing only required values which don't have defaults set
    try:
        # Create a ResourceRole
        api_response = api_instance.create_resource_role(resource_type, resource_role)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->create_resource_role: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_type** | **str**| The type of resource in the path |
 **resource_role** | [**ResourceRole**](ResourceRole.md)|  |

### Return type

[**ResourceRole**](ResourceRole.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New ResourceRole created |  -  |
**409** | An ResourceRole with the same name already exists for this resource_type. The existing ResourceRole is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_resource_permission**
> delete_resource_permission(resource_permission_id)

Delete a ResourcePermission

Delete a ResourcePermission

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    resource_permission_id = "1234" # str | A resource permission id found in the path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a ResourcePermission
        api_instance.delete_resource_permission(resource_permission_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->delete_resource_permission: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a ResourcePermission
        api_instance.delete_resource_permission(resource_permission_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->delete_resource_permission: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_permission_id** | **str**| A resource permission id found in the path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | ResourcePermission deleted |  -  |
**404** | ResourcePermission not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_resource_role**
> delete_resource_role(resource_type, role_name)

Delete a ResourceRole

Delete a ResourceRole

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    resource_type = "fileshare" # str | The type of resource in the path
    role_name = "1234" # str | A resource role name found in the path

    # example passing only required values which don't have defaults set
    try:
        # Delete a ResourceRole
        api_instance.delete_resource_role(resource_type, role_name)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->delete_resource_role: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_type** | **str**| The type of resource in the path |
 **role_name** | **str**| A resource role name found in the path |

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | ResourceRole deleted |  -  |
**404** | ResourceRole not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_elevated_user_roles**
> UserRoles get_elevated_user_roles(user_id)

Get elevated roles for a user

Get elevated roles for a user

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.user_roles import UserRoles
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    user_id = "1234" # str | user_id path

    # example passing only required values which don't have defaults set
    try:
        # Get elevated roles for a user
        api_response = api_instance.get_elevated_user_roles(user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->get_elevated_user_roles: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| user_id path |

### Return type

[**UserRoles**](UserRoles.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return elevated user roles |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_resource_permission**
> ResourcePermission get_resource_permission(resource_permission_id)

Get a ResourcePermission

Get a ResourcePermission

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.resource_permission import ResourcePermission
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    resource_permission_id = "1234" # str | A resource permission id found in the path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a ResourcePermission
        api_response = api_instance.get_resource_permission(resource_permission_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->get_resource_permission: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a ResourcePermission
        api_response = api_instance.get_resource_permission(resource_permission_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->get_resource_permission: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_permission_id** | **str**| A resource permission id found in the path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ResourcePermission**](ResourcePermission.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ResourcePermission retrieved |  -  |
**404** | ResourcePermission not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_resource_role**
> ResourceRole get_resource_role(resource_type, role_name)

Get a ResourceRole

Get a ResourceRole

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.resource_role import ResourceRole
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    resource_type = "fileshare" # str | The type of resource in the path
    role_name = "1234" # str | A resource role name found in the path

    # example passing only required values which don't have defaults set
    try:
        # Get a ResourceRole
        api_response = api_instance.get_resource_role(resource_type, role_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->get_resource_role: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_type** | **str**| The type of resource in the path |
 **role_name** | **str**| A resource role name found in the path |

### Return type

[**ResourceRole**](ResourceRole.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ResourceRole retrieved |  -  |
**404** | ResourceRole not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_elevated_user_roles**
> ListElevatedUserRoles list_elevated_user_roles()

List all elevated users and their roles

List all elevated users and their roles

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.list_elevated_user_roles import ListElevatedUserRoles
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all elevated users and their roles
        api_response = api_instance.list_elevated_user_roles(limit=limit, user_id=user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->list_elevated_user_roles: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **user_id** | **str**| Query based on user id | [optional]

### Return type

[**ListElevatedUserRoles**](ListElevatedUserRoles.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | User role updated |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_resource_permissions**
> ListResourcePermissionsResponse list_resource_permissions()

List all ResourcePermissions

List all ResourcePermissions

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.resource_type_enum import ResourceTypeEnum
from agilicus_api.model.list_resource_permissions_response import ListResourcePermissionsResponse
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    user_id = "1234" # str | Query based on user id (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    resource_type = ResourceTypeEnum("fileshare") # ResourceTypeEnum | The type of resource to query for (optional)
    resource_role_name = "owner" # str | The name of the role to query for (optional)
    resource_id = "owner" # str | The id of the resource to query for (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all ResourcePermissions
        api_response = api_instance.list_resource_permissions(limit=limit, user_id=user_id, org_id=org_id, resource_type=resource_type, resource_role_name=resource_role_name, resource_id=resource_id, page_at_id=page_at_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->list_resource_permissions: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **user_id** | **str**| Query based on user id | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **resource_type** | **ResourceTypeEnum**| The type of resource to query for | [optional]
 **resource_role_name** | **str**| The name of the role to query for | [optional]
 **resource_id** | **str**| The id of the resource to query for | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]

### Return type

[**ListResourcePermissionsResponse**](ListResourcePermissionsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Query succeeded |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_resource_roles**
> ListResourceRolesResponse list_resource_roles()

List all ResourceRoles

List all ResourceRoles

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.resource_type_enum import ResourceTypeEnum
from agilicus_api.model.list_resource_roles_response import ListResourceRolesResponse
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    resource_type = ResourceTypeEnum("fileshare") # ResourceTypeEnum | The type of resource to query for (optional)
    resource_role_name = "owner" # str | The name of the role to query for (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all ResourceRoles
        api_response = api_instance.list_resource_roles(org_id=org_id, resource_type=resource_type, resource_role_name=resource_role_name, limit=limit)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->list_resource_roles: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **resource_type** | **ResourceTypeEnum**| The type of resource to query for | [optional]
 **resource_role_name** | **str**| The name of the role to query for | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500

### Return type

[**ListResourceRolesResponse**](ListResourceRolesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Query succeeded |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_resource_roles_for_type**
> ListResourceRolesResponse list_resource_roles_for_type(resource_type)

List all ResourceRoles

List all ResourceRoles for a given resource type.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.list_resource_roles_response import ListResourceRolesResponse
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    resource_type = "fileshare" # str | The type of resource in the path
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    resource_role_name = "owner" # str | The name of the role to query for (optional)

    # example passing only required values which don't have defaults set
    try:
        # List all ResourceRoles
        api_response = api_instance.list_resource_roles_for_type(resource_type)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->list_resource_roles_for_type: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all ResourceRoles
        api_response = api_instance.list_resource_roles_for_type(resource_type, limit=limit, resource_role_name=resource_role_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->list_resource_roles_for_type: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_type** | **str**| The type of resource in the path |
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **resource_role_name** | **str**| The name of the role to query for | [optional]

### Return type

[**ListResourceRolesResponse**](ListResourceRolesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Query succeeded |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_elevated_user_role**
> replace_elevated_user_role(user_id)

Create or update an elevated user role

Create or update an elevated user role

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.replace_user_role_request import ReplaceUserRoleRequest
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    user_id = "1234" # str | user_id path
    replace_user_role_request = ReplaceUserRoleRequest(
        roles=Roles(
            key=[
                "key_example",
            ],
        ),
    ) # ReplaceUserRoleRequest |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Create or update an elevated user role
        api_instance.replace_elevated_user_role(user_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->replace_elevated_user_role: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Create or update an elevated user role
        api_instance.replace_elevated_user_role(user_id, replace_user_role_request=replace_user_role_request)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->replace_elevated_user_role: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| user_id path |
 **replace_user_role_request** | [**ReplaceUserRoleRequest**](ReplaceUserRoleRequest.md)|  | [optional]

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | User role updated |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_resource_permission**
> ResourcePermission replace_resource_permission(resource_permission_id)

Update a ResourcePermission

Update a ResourcePermission

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.resource_permission import ResourcePermission
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    resource_permission_id = "1234" # str | A resource permission id found in the path
    resource_permission = ResourcePermission(
        metadata=MetadataWithId(),
        spec=ResourcePermissionSpec(
            user_id="549sSkfdsksakSKD40",
            org_id="IAsl3dl40aSsfLKiU76",
            resource_id="s9df932aSFl48sazZ4",
            resource_type="fileshare",
            resource_role_name="fileshare",
        ),
    ) # ResourcePermission |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update a ResourcePermission
        api_response = api_instance.replace_resource_permission(resource_permission_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->replace_resource_permission: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a ResourcePermission
        api_response = api_instance.replace_resource_permission(resource_permission_id, resource_permission=resource_permission)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->replace_resource_permission: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_permission_id** | **str**| A resource permission id found in the path |
 **resource_permission** | [**ResourcePermission**](ResourcePermission.md)|  | [optional]

### Return type

[**ResourcePermission**](ResourcePermission.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ResourcePermission updated |  -  |
**404** | ResourcePermission not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_resource_role**
> ResourceRole replace_resource_role(resource_type, role_name)

Update a ResourceRole

Update a ResourceRole

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import permissions_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.resource_role import ResourceRole
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = permissions_api.PermissionsApi(api_client)
    resource_type = "fileshare" # str | The type of resource in the path
    role_name = "1234" # str | A resource role name found in the path
    resource_role = ResourceRole(
        metadata=MetadataWithId(),
        spec=ResourceRoleSpec(
            resource_type="fileshare",
            role_name="owner",
            description="Provides full access to the the file share.",
        ),
    ) # ResourceRole |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update a ResourceRole
        api_response = api_instance.replace_resource_role(resource_type, role_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->replace_resource_role: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a ResourceRole
        api_response = api_instance.replace_resource_role(resource_type, role_name, resource_role=resource_role)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PermissionsApi->replace_resource_role: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **resource_type** | **str**| The type of resource in the path |
 **role_name** | **str**| A resource role name found in the path |
 **resource_role** | [**ResourceRole**](ResourceRole.md)|  | [optional]

### Return type

[**ResourceRole**](ResourceRole.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | ResourceRole updated |  -  |
**404** | ResourceRole not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

