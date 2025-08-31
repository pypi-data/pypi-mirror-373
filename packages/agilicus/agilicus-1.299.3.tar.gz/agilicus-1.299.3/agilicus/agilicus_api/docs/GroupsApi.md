# agilicus_api.GroupsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_group_member**](GroupsApi.md#add_group_member) | **POST** /v1/groups/{group_id}/members | Add a group member
[**create_group**](GroupsApi.md#create_group) | **POST** /v1/groups | Create a group
[**create_upstream_group_reconcile**](GroupsApi.md#create_upstream_group_reconcile) | **POST** /v1/groups/reconcile_upstream_groups | Reconcile a user&#39;s groups based on the user&#39;s upstream group membership
[**create_upstream_group_reconcile_sim**](GroupsApi.md#create_upstream_group_reconcile_sim) | **POST** /v1/groups/simulate_reconcile_upstream_groups | Get the set of groups to reconcile based on the user&#39;s upstream group membership
[**delete_group**](GroupsApi.md#delete_group) | **DELETE** /v1/groups/{group_id} | Delete a group
[**delete_group_member**](GroupsApi.md#delete_group_member) | **DELETE** /v1/groups/{group_id}/members/{member_id} | Remove a group member
[**get_group**](GroupsApi.md#get_group) | **GET** /v1/groups/{group_id} | Get a group
[**list_groups**](GroupsApi.md#list_groups) | **GET** /v1/groups | Get all groups
[**replace_group**](GroupsApi.md#replace_group) | **PUT** /v1/groups/{group_id} | update a group


# **add_group_member**
> User add_group_member(group_id, add_group_member_request)

Add a group member

Add a group member

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import groups_api
from agilicus_api.model.user import User
from agilicus_api.model.add_group_member_request import AddGroupMemberRequest
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
    api_instance = groups_api.GroupsApi(api_client)
    group_id = "1234" # str | group_id path
    add_group_member_request = AddGroupMemberRequest(
        id="123",
        org_id="123",
        member_id="123",
        member_org_id="123",
        email=Email("foo@example.com"),
        upstream_issuer="https://login.microsoftonline.com/c945d377-ea94-4a7d-9c83-0615e7ff0022/v2.0",
    ) # AddGroupMemberRequest | 

    # example passing only required values which don't have defaults set
    try:
        # Add a group member
        api_response = api_instance.add_group_member(group_id, add_group_member_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->add_group_member: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**| group_id path |
 **add_group_member_request** | [**AddGroupMemberRequest**](AddGroupMemberRequest.md)|  |

### Return type

[**User**](User.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New group member added |  -  |
**409** | Group member already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_group**
> Group create_group(group)

Create a group

Create a group

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import groups_api
from agilicus_api.model.group import Group
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
    api_instance = groups_api.GroupsApi(api_client)
    group = Group() # Group | 

    # example passing only required values which don't have defaults set
    try:
        # Create a group
        api_response = api_instance.create_group(group)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->create_group: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group** | [**Group**](Group.md)|  |

### Return type

[**Group**](Group.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New group created |  -  |
**409** | Group already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_upstream_group_reconcile**
> UpstreamGroupReconcileResponse create_upstream_group_reconcile(upstream_group_reconcile)

Reconcile a user's groups based on the user's upstream group membership

Reconcile a user's groups based on the user's upstream group membership

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import groups_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.upstream_group_reconcile_response import UpstreamGroupReconcileResponse
from agilicus_api.model.upstream_group_reconcile import UpstreamGroupReconcile
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
    api_instance = groups_api.GroupsApi(api_client)
    upstream_group_reconcile = UpstreamGroupReconcile(
        user_id="tuU7smH86zAXMl76sua6xQ",
        org_id="IAsl3dl40aSsfLKiU76",
        mapping=UpstreamGroupMapping(
            metadata=MetadataWithId(),
            spec=UpstreamGroupMappingSpec(
                upstream_issuer="https://login.microsoftonline.com/c945d377-ea94-4a7d-9c83-0615e7ff0022/v2.0",
                org_id="asdfg123hjkl",
                group_mappings=[
                    UpstreamGroupMappingEntry(
                        priority=1,
                        upstream_group_name="Company Team (.*)",
                        upstream_name_is_a_guid=False,
                        agilicus_group_name="Agilicus {0}",
                        group_org_id="asdfg123hjkl",
                    ),
                ],
                excluded_groups=[
                    UpstreamGroupExcludedEntry(
                        upstream_group_name="Admin*",
                        upstream_name_is_a_guid=False,
                    ),
                ],
            ),
        ),
        group_names_from_upstream=[
            "group_names_from_upstream_example",
        ],
        group_guids_from_upstream=[
            "group_guids_from_upstream_example",
        ],
    ) # UpstreamGroupReconcile | 

    # example passing only required values which don't have defaults set
    try:
        # Reconcile a user's groups based on the user's upstream group membership
        api_response = api_instance.create_upstream_group_reconcile(upstream_group_reconcile)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->create_upstream_group_reconcile: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upstream_group_reconcile** | [**UpstreamGroupReconcile**](UpstreamGroupReconcile.md)|  |

### Return type

[**UpstreamGroupReconcileResponse**](UpstreamGroupReconcileResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return group mapping |  -  |
**400** | An error occured, check the message for further details |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_upstream_group_reconcile_sim**
> UpstreamGroupReconcileResponse create_upstream_group_reconcile_sim(upstream_group_reconcile)

Get the set of groups to reconcile based on the user's upstream group membership

Get the set of groups to reconcile based on the user's upstream group membership This indicates what reconciliatory action will be taken if this endpoint is invoked via a POST. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import groups_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.upstream_group_reconcile_response import UpstreamGroupReconcileResponse
from agilicus_api.model.upstream_group_reconcile import UpstreamGroupReconcile
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
    api_instance = groups_api.GroupsApi(api_client)
    upstream_group_reconcile = UpstreamGroupReconcile(
        user_id="tuU7smH86zAXMl76sua6xQ",
        org_id="IAsl3dl40aSsfLKiU76",
        mapping=UpstreamGroupMapping(
            metadata=MetadataWithId(),
            spec=UpstreamGroupMappingSpec(
                upstream_issuer="https://login.microsoftonline.com/c945d377-ea94-4a7d-9c83-0615e7ff0022/v2.0",
                org_id="asdfg123hjkl",
                group_mappings=[
                    UpstreamGroupMappingEntry(
                        priority=1,
                        upstream_group_name="Company Team (.*)",
                        upstream_name_is_a_guid=False,
                        agilicus_group_name="Agilicus {0}",
                        group_org_id="asdfg123hjkl",
                    ),
                ],
                excluded_groups=[
                    UpstreamGroupExcludedEntry(
                        upstream_group_name="Admin*",
                        upstream_name_is_a_guid=False,
                    ),
                ],
            ),
        ),
        group_names_from_upstream=[
            "group_names_from_upstream_example",
        ],
        group_guids_from_upstream=[
            "group_guids_from_upstream_example",
        ],
    ) # UpstreamGroupReconcile | 

    # example passing only required values which don't have defaults set
    try:
        # Get the set of groups to reconcile based on the user's upstream group membership
        api_response = api_instance.create_upstream_group_reconcile_sim(upstream_group_reconcile)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->create_upstream_group_reconcile_sim: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upstream_group_reconcile** | [**UpstreamGroupReconcile**](UpstreamGroupReconcile.md)|  |

### Return type

[**UpstreamGroupReconcileResponse**](UpstreamGroupReconcileResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return group mapping |  -  |
**400** | An error occured, check the message for further details |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_group**
> delete_group(group_id)

Delete a group

Delete a group

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import groups_api
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
    api_instance = groups_api.GroupsApi(api_client)
    group_id = "1234" # str | group_id path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a group
        api_instance.delete_group(group_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->delete_group: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a group
        api_instance.delete_group(group_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->delete_group: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**| group_id path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Group was deleted |  -  |
**404** | Group does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_group_member**
> delete_group_member(group_id, member_id)

Remove a group member

Remove a group member

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import groups_api
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
    api_instance = groups_api.GroupsApi(api_client)
    group_id = "1234" # str | group_id path
    member_id = "1234" # str | member_id path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Remove a group member
        api_instance.delete_group_member(group_id, member_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->delete_group_member: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Remove a group member
        api_instance.delete_group_member(group_id, member_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->delete_group_member: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**| group_id path |
 **member_id** | **str**| member_id path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | member was removed |  -  |
**404** | group or member does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_group**
> Group get_group(group_id)

Get a group

Get a group

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import groups_api
from agilicus_api.model.group import Group
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
    api_instance = groups_api.GroupsApi(api_client)
    group_id = "1234" # str | group_id path
    org_id = "1234" # str | Organisation Unique identifier (optional)
    flatten_hierarchy = True # bool | Return the object with the full list of child members  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a group
        api_response = api_instance.get_group(group_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->get_group: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a group
        api_response = api_instance.get_group(group_id, org_id=org_id, flatten_hierarchy=flatten_hierarchy)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->get_group: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**| group_id path |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **flatten_hierarchy** | **bool**| Return the object with the full list of child members  | [optional]

### Return type

[**Group**](Group.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return group |  -  |
**404** | Group does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_groups**
> ListGroupsResponse list_groups()

Get all groups

Get all groups

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import groups_api
from agilicus_api.model.list_groups_response import ListGroupsResponse
from agilicus_api.model.email import Email
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
    api_instance = groups_api.GroupsApi(api_client)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    type = ["group"] # [str] | The type of groups to search for. Multiple values are ORed together. (optional) if omitted the server will use the default value of ["group"]
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    previous_email = Email("foo@example.com") # Email | Pagination based query with the user's email as the key. To get the initial entries supply an empty string. (optional)
    search_direction = "forwards" # str | Direction which the search should go starting from the email_nullable_query parameter.  (optional) if omitted the server will use the default value of "forwards"
    prefix_email_search = Email("Foo") # Email | Keyword used to search for a list of users based on email. This parameter is case insensitive and finds users with an email that matches the keyword by its prefix. For example, if the keyword \"Foo\" is supplied to this parameter, users with emails of \"foo1@example.com\" and \"Foo2@test.com\" could be returned.  (optional)
    allow_partial_match = True # bool | Perform a case insensitive partial match of any string query parameters included in the query  (optional)
    first_name = "John" # str | query for users with a first name that matches the query parameter (optional)
    last_name = "Smith" # str | query for users with a last name that matches the query parameter (optional)
    search_params = [
        "mat",
    ] # [str] | A list of strings to perform a case-insensitive search on all relevant fields in the database for a given collection. Multiple values are ANDed together  (optional)
    show_system_user = True # bool | If set to false, query users that have is_system_user set to False.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all groups
        api_response = api_instance.list_groups(org_id=org_id, type=type, limit=limit, previous_email=previous_email, search_direction=search_direction, prefix_email_search=prefix_email_search, allow_partial_match=allow_partial_match, first_name=first_name, last_name=last_name, search_params=search_params, show_system_user=show_system_user)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->list_groups: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **type** | **[str]**| The type of groups to search for. Multiple values are ORed together. | [optional] if omitted the server will use the default value of ["group"]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **previous_email** | **Email**| Pagination based query with the user&#39;s email as the key. To get the initial entries supply an empty string. | [optional]
 **search_direction** | **str**| Direction which the search should go starting from the email_nullable_query parameter.  | [optional] if omitted the server will use the default value of "forwards"
 **prefix_email_search** | **Email**| Keyword used to search for a list of users based on email. This parameter is case insensitive and finds users with an email that matches the keyword by its prefix. For example, if the keyword \&quot;Foo\&quot; is supplied to this parameter, users with emails of \&quot;foo1@example.com\&quot; and \&quot;Foo2@test.com\&quot; could be returned.  | [optional]
 **allow_partial_match** | **bool**| Perform a case insensitive partial match of any string query parameters included in the query  | [optional]
 **first_name** | **str**| query for users with a first name that matches the query parameter | [optional]
 **last_name** | **str**| query for users with a last name that matches the query parameter | [optional]
 **search_params** | **[str]**| A list of strings to perform a case-insensitive search on all relevant fields in the database for a given collection. Multiple values are ANDed together  | [optional]
 **show_system_user** | **bool**| If set to false, query users that have is_system_user set to False.  | [optional]

### Return type

[**ListGroupsResponse**](ListGroupsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return groups |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_group**
> Group replace_group(group_id)

update a group

update a group

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import groups_api
from agilicus_api.model.group import Group
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
    api_instance = groups_api.GroupsApi(api_client)
    group_id = "1234" # str | group_id path
    group = Group() # Group |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a group
        api_response = api_instance.replace_group(group_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->replace_group: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a group
        api_response = api_instance.replace_group(group_id, group=group)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling GroupsApi->replace_group: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **str**| group_id path |
 **group** | [**Group**](Group.md)|  | [optional]

### Return type

[**Group**](Group.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated group |  -  |
**404** | group does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

