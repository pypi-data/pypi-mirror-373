# agilicus_api.LabelsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_delete_labelled_objects**](LabelsApi.md#bulk_delete_labelled_objects) | **POST** /v1/labelled_objects/bulk_delete | Delete many label associations
[**create_labelled_object**](LabelsApi.md#create_labelled_object) | **POST** /v1/labelled_objects | Add a labelled object
[**create_labelled_object_label**](LabelsApi.md#create_labelled_object_label) | **POST** /v1/labelled_objects/{labelled_object_id}/labels | Add a label association
[**create_object_label**](LabelsApi.md#create_object_label) | **POST** /v1/labels | Add a label
[**delete_labelled_object**](LabelsApi.md#delete_labelled_object) | **DELETE** /v1/labelled_objects/{labelled_object_id} | Delete a labelled object
[**delete_labelled_object_label**](LabelsApi.md#delete_labelled_object_label) | **DELETE** /v1/labelled_objects/{labelled_object_id}/labels/{label_name} | Delete a label association
[**delete_object_label**](LabelsApi.md#delete_object_label) | **DELETE** /v1/labels/{label_id} | Delete a label
[**get_labelled_object**](LabelsApi.md#get_labelled_object) | **GET** /v1/labelled_objects/{labelled_object_id} | Get a labelled object
[**get_object_label**](LabelsApi.md#get_object_label) | **GET** /v1/labels/{label_id} | Get a label
[**list_labelled_objects**](LabelsApi.md#list_labelled_objects) | **GET** /v1/labelled_objects | List all labelled objects
[**list_object_labels**](LabelsApi.md#list_object_labels) | **GET** /v1/labels | List all labels
[**replace_labelled_object**](LabelsApi.md#replace_labelled_object) | **PUT** /v1/labelled_objects/{labelled_object_id} | update a labelled object
[**replace_object_label**](LabelsApi.md#replace_object_label) | **PUT** /v1/labels/{label_id} | update a label


# **bulk_delete_labelled_objects**
> BulkDeleteLabelledObjectsResponse bulk_delete_labelled_objects(bulk_delete_labelled_objects_request)

Delete many label associations

Deletes many label associations. Will also remove any labels if they are no longer referenced and they were automatically created. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.bulk_delete_labelled_objects_request import BulkDeleteLabelledObjectsRequest
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.bulk_delete_labelled_objects_response import BulkDeleteLabelledObjectsResponse
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
    api_instance = labels_api.LabelsApi(api_client)
    bulk_delete_labelled_objects_request = BulkDeleteLabelledObjectsRequest(
        org_id="123",
        object_ids=[
            "123",
        ],
    ) # BulkDeleteLabelledObjectsRequest | 

    # example passing only required values which don't have defaults set
    try:
        # Delete many label associations
        api_response = api_instance.bulk_delete_labelled_objects(bulk_delete_labelled_objects_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->bulk_delete_labelled_objects: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bulk_delete_labelled_objects_request** | [**BulkDeleteLabelledObjectsRequest**](BulkDeleteLabelledObjectsRequest.md)|  |

### Return type

[**BulkDeleteLabelledObjectsResponse**](BulkDeleteLabelledObjectsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | LabelledObjects deleted |  -  |
**400** | The request is invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_labelled_object**
> LabelledObject create_labelled_object(labelled_object)

Add a labelled object

Adds a new labelled object. The association must have a unique object_id, object_type and label_name within an organsation. If it does not, then the create will return a 409 including the conflicting object. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.labelled_object import LabelledObject
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
    api_instance = labels_api.LabelsApi(api_client)
    labelled_object = LabelledObject(
        object_id="123",
        object_type=ObjectType("desktop"),
        labels=[
            LabelAssociation(
                label_name=LabelName("site-A"),
                org_id="123",
                status=LabelAssociationStatus(
                    navigation=LabelNavigation(
                        enabled=True,
                    ),
                ),
            ),
        ],
        org_id="123",
    ) # LabelledObject | 

    # example passing only required values which don't have defaults set
    try:
        # Add a labelled object
        api_response = api_instance.create_labelled_object(labelled_object)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->create_labelled_object: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **labelled_object** | [**LabelledObject**](LabelledObject.md)|  |

### Return type

[**LabelledObject**](LabelledObject.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New labelled object created. |  -  |
**400** | The request is invalid |  -  |
**409** | labelled object already exists. The existing labelled object is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_labelled_object_label**
> LabelAssociation create_labelled_object_label(labelled_object_id, label_association)

Add a label association

Associates a label with an object. If already associated, this will return a 409 including the conflicting object. Note that a new label will be created if one with the provided name does not yet exist. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.label_association import LabelAssociation
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
    api_instance = labels_api.LabelsApi(api_client)
    labelled_object_id = "x9x7aD" # str | A labelled object ID
    label_association = LabelAssociation(
        label_name=LabelName("site-A"),
        org_id="123",
        status=LabelAssociationStatus(
            navigation=LabelNavigation(
                enabled=True,
            ),
        ),
    ) # LabelAssociation | 

    # example passing only required values which don't have defaults set
    try:
        # Add a label association
        api_response = api_instance.create_labelled_object_label(labelled_object_id, label_association)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->create_labelled_object_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **labelled_object_id** | **str**| A labelled object ID |
 **label_association** | [**LabelAssociation**](LabelAssociation.md)|  |

### Return type

[**LabelAssociation**](LabelAssociation.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New label association created. |  -  |
**400** | The request is invalid |  -  |
**409** | label association already exists. The existing label association is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_object_label**
> Label create_object_label(label)

Add a label

Adds a label. Labels must have unique names within an org. If the name is not unique, a 409 will be returned. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.label import Label
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
    api_instance = labels_api.LabelsApi(api_client)
    label = Label(
        metadata=MetadataWithId(),
        spec=LabelSpec(
            name=LabelName("site-A"),
            org_id="123",
            description="identifies items in Site A",
            navigation=LabelNavigation(
                enabled=True,
            ),
            display_info=DisplayInfo(
                icons=[
                    Icon(
                        uri="https://storage.googleapis.com/agilicus/logo.svg",
                        purposes=[
                            IconPurpose("agilicus-launcher"),
                        ],
                        dimensions=IconDimensions(
                            width=32,
                            height=32,
                        ),
                    ),
                ],
                hide="no",
            ),
        ),
    ) # Label | 

    # example passing only required values which don't have defaults set
    try:
        # Add a label
        api_response = api_instance.create_object_label(label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->create_object_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **label** | [**Label**](Label.md)|  |

### Return type

[**Label**](Label.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New label created. |  -  |
**400** | The request is invalid |  -  |
**409** | label already exists. The existing label is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_labelled_object**
> delete_labelled_object(labelled_object_id)

Delete a labelled object

Delete a labelled object

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
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
    api_instance = labels_api.LabelsApi(api_client)
    labelled_object_id = "x9x7aD" # str | A labelled object ID
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a labelled object
        api_instance.delete_labelled_object(labelled_object_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->delete_labelled_object: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a labelled object
        api_instance.delete_labelled_object(labelled_object_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->delete_labelled_object: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **labelled_object_id** | **str**| A labelled object ID |
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
**204** | LabelledObject was deleted |  -  |
**404** | LabelledObject does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_labelled_object_label**
> delete_labelled_object_label(labelled_object_id, label_name)

Delete a label association

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.label_name import LabelName
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
    api_instance = labels_api.LabelsApi(api_client)
    labelled_object_id = "x9x7aD" # str | A labelled object ID
    label_name = LabelName("site-a") # LabelName | A label name
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a label association
        api_instance.delete_labelled_object_label(labelled_object_id, label_name)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->delete_labelled_object_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a label association
        api_instance.delete_labelled_object_label(labelled_object_id, label_name, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->delete_labelled_object_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **labelled_object_id** | **str**| A labelled object ID |
 **label_name** | **LabelName**| A label name |
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
**204** | LabelAssociation was deleted |  -  |
**404** | LabelAssociation does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_object_label**
> delete_object_label(label_id)

Delete a label

Delete a label

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
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
    api_instance = labels_api.LabelsApi(api_client)
    label_id = "x9x7aD" # str | A label Id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a label
        api_instance.delete_object_label(label_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->delete_object_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a label
        api_instance.delete_object_label(label_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->delete_object_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **label_id** | **str**| A label Id |
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
**204** | Label was deleted |  -  |
**404** | Label does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_labelled_object**
> LabelledObject get_labelled_object(labelled_object_id)

Get a labelled object

Get a labelled object

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.labelled_object import LabelledObject
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
    api_instance = labels_api.LabelsApi(api_client)
    labelled_object_id = "x9x7aD" # str | A labelled object ID
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a labelled object
        api_response = api_instance.get_labelled_object(labelled_object_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->get_labelled_object: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a labelled object
        api_response = api_instance.get_labelled_object(labelled_object_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->get_labelled_object: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **labelled_object_id** | **str**| A labelled object ID |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**LabelledObject**](LabelledObject.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a LabelledObject |  -  |
**404** | LabelledObject does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_object_label**
> Label get_object_label(label_id)

Get a label

Get a label

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.label import Label
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
    api_instance = labels_api.LabelsApi(api_client)
    label_id = "x9x7aD" # str | A label Id
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a label
        api_response = api_instance.get_object_label(label_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->get_object_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a label
        api_response = api_instance.get_object_label(label_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->get_object_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **label_id** | **str**| A label Id |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**Label**](Label.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a Label |  -  |
**404** | Label does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_labelled_objects**
> ListLabelledObjectsResponse list_labelled_objects()

List all labelled objects

List all labelled objects matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. Searching for label_id will return any tree that references that label. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.object_type import ObjectType
from agilicus_api.model.label_name import LabelName
from agilicus_api.model.list_labelled_objects_response import ListLabelledObjectsResponse
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
    api_instance = labels_api.LabelsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    includes_any_label = [
        LabelName("["site-a"]"),
    ] # [LabelName] | A list of labels to match against. Matches objects with any of the labels (optional)
    excludes_any_label = [
        LabelName("["site-a"]"),
    ] # [LabelName] | A list of labels to match against. Matches objects with none of the labels (optional)
    object_id = "1234" # str | search by object id (optional)
    object_type = ObjectType("abA12") # ObjectType | An object type (optional)
    object_types = [
        ObjectType("["abA12"]"),
    ] # [ObjectType] | A list of object types. Returns all items which match at least one of the types.  (optional)
    object_ids = ["aba23"] # [str] | A list of object IDs. Returns all items which match at least one of the .  (optional)
    org_ids = ["q20sd0dfs3llasd0af9"] # [str] | The list of org ids to search for. Each org will be searched for independently. (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all labelled objects
        api_response = api_instance.list_labelled_objects(limit=limit, includes_any_label=includes_any_label, excludes_any_label=excludes_any_label, object_id=object_id, object_type=object_type, object_types=object_types, object_ids=object_ids, org_ids=org_ids, page_at_id=page_at_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->list_labelled_objects: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **includes_any_label** | [**[LabelName]**](LabelName.md)| A list of labels to match against. Matches objects with any of the labels | [optional]
 **excludes_any_label** | [**[LabelName]**](LabelName.md)| A list of labels to match against. Matches objects with none of the labels | [optional]
 **object_id** | **str**| search by object id | [optional]
 **object_type** | **ObjectType**| An object type | [optional]
 **object_types** | [**[ObjectType]**](ObjectType.md)| A list of object types. Returns all items which match at least one of the types.  | [optional]
 **object_ids** | **[str]**| A list of object IDs. Returns all items which match at least one of the .  | [optional]
 **org_ids** | **[str]**| The list of org ids to search for. Each org will be searched for independently. | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**ListLabelledObjectsResponse**](ListLabelledObjectsResponse.md)

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

# **list_object_labels**
> ListLabelsResponse list_object_labels()

List all labels

List all labels matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.list_labels_response import ListLabelsResponse
from agilicus_api.model.label_name import LabelName
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
    api_instance = labels_api.LabelsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    label_name = LabelName("site-a") # LabelName | A label name (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    navigation_enabled = True # bool | Only return labels used for navigation (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all labels
        api_response = api_instance.list_object_labels(limit=limit, label_name=label_name, page_at_id=page_at_id, org_id=org_id, navigation_enabled=navigation_enabled)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->list_object_labels: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **label_name** | **LabelName**| A label name | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **navigation_enabled** | **bool**| Only return labels used for navigation | [optional]

### Return type

[**ListLabelsResponse**](ListLabelsResponse.md)

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

# **replace_labelled_object**
> LabelledObject replace_labelled_object(labelled_object_id)

update a labelled object

update a labelled object

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.labelled_object import LabelledObject
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
    api_instance = labels_api.LabelsApi(api_client)
    labelled_object_id = "x9x7aD" # str | A labelled object ID
    labelled_object = LabelledObject(
        object_id="123",
        object_type=ObjectType("desktop"),
        labels=[
            LabelAssociation(
                label_name=LabelName("site-A"),
                org_id="123",
                status=LabelAssociationStatus(
                    navigation=LabelNavigation(
                        enabled=True,
                    ),
                ),
            ),
        ],
        org_id="123",
    ) # LabelledObject |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a labelled object
        api_response = api_instance.replace_labelled_object(labelled_object_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->replace_labelled_object: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a labelled object
        api_response = api_instance.replace_labelled_object(labelled_object_id, labelled_object=labelled_object)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->replace_labelled_object: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **labelled_object_id** | **str**| A labelled object ID |
 **labelled_object** | [**LabelledObject**](LabelledObject.md)|  | [optional]

### Return type

[**LabelledObject**](LabelledObject.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated LabelledObject |  -  |
**400** | The request is invalid |  -  |
**404** | LabelledObject does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_object_label**
> Label replace_object_label(label_id)

update a label

update a label

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import labels_api
from agilicus_api.model.label import Label
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
    api_instance = labels_api.LabelsApi(api_client)
    label_id = "x9x7aD" # str | A label Id
    label = Label(
        metadata=MetadataWithId(),
        spec=LabelSpec(
            name=LabelName("site-A"),
            org_id="123",
            description="identifies items in Site A",
            navigation=LabelNavigation(
                enabled=True,
            ),
            display_info=DisplayInfo(
                icons=[
                    Icon(
                        uri="https://storage.googleapis.com/agilicus/logo.svg",
                        purposes=[
                            IconPurpose("agilicus-launcher"),
                        ],
                        dimensions=IconDimensions(
                            width=32,
                            height=32,
                        ),
                    ),
                ],
                hide="no",
            ),
        ),
    ) # Label |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a label
        api_response = api_instance.replace_object_label(label_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->replace_object_label: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a label
        api_response = api_instance.replace_object_label(label_id, label=label)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LabelsApi->replace_object_label: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **label_id** | **str**| A label Id |
 **label** | [**Label**](Label.md)|  | [optional]

### Return type

[**Label**](Label.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated Label |  -  |
**400** | The request is invalid |  -  |
**404** | Label does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

