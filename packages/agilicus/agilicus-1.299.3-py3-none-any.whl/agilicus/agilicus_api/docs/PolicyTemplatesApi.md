# agilicus_api.PolicyTemplatesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_policy_template_instance**](PolicyTemplatesApi.md#create_policy_template_instance) | **POST** /v1/policy_template_instances | Add a PolicyTemplateInstance
[**delete_policy_template_instance**](PolicyTemplatesApi.md#delete_policy_template_instance) | **DELETE** /v1/policy_template_instances/{instance_id} | Delete a PolicyTemplateInstance
[**get_policy_template_instance**](PolicyTemplatesApi.md#get_policy_template_instance) | **GET** /v1/policy_template_instances/{instance_id} | Get a PolicyTemplateInstance
[**list_policy_template_instances**](PolicyTemplatesApi.md#list_policy_template_instances) | **GET** /v1/policy_template_instances | List all standalone policy_templates
[**replace_policy_template_instance**](PolicyTemplatesApi.md#replace_policy_template_instance) | **PUT** /v1/policy_template_instances/{instance_id} | update a PolicyTemplateInstance


# **create_policy_template_instance**
> PolicyTemplateInstance create_policy_template_instance(policy_template_instance)

Add a PolicyTemplateInstance

Adds a new PolicyTemplateInstance. PolicyTemplates must have unique names within an org for a particular type of template. If the name is not unique, a 409 will be returned. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import policy_templates_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.policy_template_instance import PolicyTemplateInstance
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
    api_instance = policy_templates_api.PolicyTemplatesApi(api_client)
    policy_template_instance = PolicyTemplateInstance(
        metadata=MetadataWithId(),
        spec=PolicyTemplateInstanceSpec(
            org_id="123",
            template=PolicyTemplate(
                template_type="InvalidPolicyTemplate",
                original_template_type="mfa",
            ),
            description="Restrict access to sensitive resources",
            name="2",
            priority=0,
            object_id="123",
            object_type=EmptiableObjectType("desktop"),
        ),
    ) # PolicyTemplateInstance | 

    # example passing only required values which don't have defaults set
    try:
        # Add a PolicyTemplateInstance
        api_response = api_instance.create_policy_template_instance(policy_template_instance)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyTemplatesApi->create_policy_template_instance: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_template_instance** | [**PolicyTemplateInstance**](PolicyTemplateInstance.md)|  |

### Return type

[**PolicyTemplateInstance**](PolicyTemplateInstance.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New PolicyTemplateInstance created. |  -  |
**400** | The request is invalid |  -  |
**409** | PolicyTemplateInstance already exists. The existing template is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_policy_template_instance**
> delete_policy_template_instance(instance_id)

Delete a PolicyTemplateInstance

Delete a PolicyTemplateInstance

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import policy_templates_api
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
    api_instance = policy_templates_api.PolicyTemplatesApi(api_client)
    instance_id = "sensitive" # str | The id of the instance to manipulate/get
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a PolicyTemplateInstance
        api_instance.delete_policy_template_instance(instance_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyTemplatesApi->delete_policy_template_instance: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a PolicyTemplateInstance
        api_instance.delete_policy_template_instance(instance_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyTemplatesApi->delete_policy_template_instance: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **instance_id** | **str**| The id of the instance to manipulate/get |
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
**204** | PolicyTemplateInstance was deleted |  -  |
**404** | PolicyTemplateInstance does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_policy_template_instance**
> PolicyTemplateInstance get_policy_template_instance(instance_id)

Get a PolicyTemplateInstance

Get a PolicyTemplateInstance

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import policy_templates_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.policy_template_instance import PolicyTemplateInstance
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
    api_instance = policy_templates_api.PolicyTemplatesApi(api_client)
    instance_id = "sensitive" # str | The id of the instance to manipulate/get
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a PolicyTemplateInstance
        api_response = api_instance.get_policy_template_instance(instance_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyTemplatesApi->get_policy_template_instance: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a PolicyTemplateInstance
        api_response = api_instance.get_policy_template_instance(instance_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyTemplatesApi->get_policy_template_instance: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **instance_id** | **str**| The id of the instance to manipulate/get |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**PolicyTemplateInstance**](PolicyTemplateInstance.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a PolicyTemplateInstance |  -  |
**404** | PolicyTemplateInstance does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_policy_template_instances**
> ListPolicyTemplateInstancesResponse list_policy_template_instances()

List all standalone policy_templates

List all PolicyTemplateInstances matching the provided query parameters. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import policy_templates_api
from agilicus_api.model.object_type import ObjectType
from agilicus_api.model.list_policy_template_instances_response import ListPolicyTemplateInstancesResponse
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
    api_instance = policy_templates_api.PolicyTemplatesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    name = "name-1" # str | Filters based on whether or not the items in the collection have the given name.  (optional)
    include_invalid = True # bool | Includes invalid templates so that they may be cleaned up  (optional)
    template_type = "mfa" # str | filters based on the template type  (optional)
    template_types = ["mfa"] # [str] | filters based on a list of template types.  (optional)
    object_id = "1234" # str | search by object id (optional)
    object_type = ObjectType("abA12") # ObjectType | An object type (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all standalone policy_templates
        api_response = api_instance.list_policy_template_instances(limit=limit, name=name, include_invalid=include_invalid, template_type=template_type, template_types=template_types, object_id=object_id, object_type=object_type, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyTemplatesApi->list_policy_template_instances: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **name** | **str**| Filters based on whether or not the items in the collection have the given name.  | [optional]
 **include_invalid** | **bool**| Includes invalid templates so that they may be cleaned up  | [optional]
 **template_type** | **str**| filters based on the template type  | [optional]
 **template_types** | **[str]**| filters based on a list of template types.  | [optional]
 **object_id** | **str**| search by object id | [optional]
 **object_type** | **ObjectType**| An object type | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListPolicyTemplateInstancesResponse**](ListPolicyTemplateInstancesResponse.md)

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

# **replace_policy_template_instance**
> PolicyTemplateInstance replace_policy_template_instance(instance_id)

update a PolicyTemplateInstance

update a PolicyTemplateInstance

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import policy_templates_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.policy_template_instance import PolicyTemplateInstance
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
    api_instance = policy_templates_api.PolicyTemplatesApi(api_client)
    instance_id = "sensitive" # str | The id of the instance to manipulate/get
    policy_template_instance = PolicyTemplateInstance(
        metadata=MetadataWithId(),
        spec=PolicyTemplateInstanceSpec(
            org_id="123",
            template=PolicyTemplate(
                template_type="InvalidPolicyTemplate",
                original_template_type="mfa",
            ),
            description="Restrict access to sensitive resources",
            name="2",
            priority=0,
            object_id="123",
            object_type=EmptiableObjectType("desktop"),
        ),
    ) # PolicyTemplateInstance |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a PolicyTemplateInstance
        api_response = api_instance.replace_policy_template_instance(instance_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyTemplatesApi->replace_policy_template_instance: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a PolicyTemplateInstance
        api_response = api_instance.replace_policy_template_instance(instance_id, policy_template_instance=policy_template_instance)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyTemplatesApi->replace_policy_template_instance: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **instance_id** | **str**| The id of the instance to manipulate/get |
 **policy_template_instance** | [**PolicyTemplateInstance**](PolicyTemplateInstance.md)|  | [optional]

### Return type

[**PolicyTemplateInstance**](PolicyTemplateInstance.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated PolicyTemplateInstance |  -  |
**400** | The request is invalid |  -  |
**404** | PolicyTemplateInstance does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

