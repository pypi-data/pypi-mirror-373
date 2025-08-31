# agilicus_api.MessagesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_delete_messages**](MessagesApi.md#bulk_delete_messages) | **POST** /v1/messages/bulk_delete | Delete a list of messages and inbox items asociated to it.
[**create_message**](MessagesApi.md#create_message) | **POST** /v1/messages/{message_endpoint_id}/send | Send a message to a specific message endpoint.
[**create_routed_message**](MessagesApi.md#create_routed_message) | **POST** /v1/messages/send_routed | Send one or more messages, letting the system choose how to deliver it
[**create_user_message**](MessagesApi.md#create_user_message) | **POST** /v1/messages/user/{user_id}/send | Send a message to a user on all (optionally of a type) endpoints.
[**delete_inbox_item**](MessagesApi.md#delete_inbox_item) | **DELETE** /v1/inboxes/{user_id}/items/{inbox_item_id} | Delete an inbox item
[**delete_message_endpoint**](MessagesApi.md#delete_message_endpoint) | **DELETE** /v1/messages/{message_endpoint_id} | Delete a messaging endpoint
[**get_inbox_item**](MessagesApi.md#get_inbox_item) | **GET** /v1/inboxes/{user_id}/items/{inbox_item_id} | Get an inbox item
[**get_message_endpoint**](MessagesApi.md#get_message_endpoint) | **GET** /v1/messages/{message_endpoint_id} | Get a message endpoint
[**list_inbox_items**](MessagesApi.md#list_inbox_items) | **GET** /v1/inboxes/{user_id}/items | Get a list of inbox items items and information about the inbox
[**list_message_endpoints**](MessagesApi.md#list_message_endpoints) | **GET** /v1/messages | List all message endpoints (all users or a single user)
[**list_messages_config**](MessagesApi.md#list_messages_config) | **GET** /v1/messages/config | Get the config of the endpoint-types (e.g. public keys etc).
[**replace_inbox_item**](MessagesApi.md#replace_inbox_item) | **PUT** /v1/inboxes/{user_id}/items/{inbox_item_id} | replace an inbox item
[**replace_message_endpoint**](MessagesApi.md#replace_message_endpoint) | **PUT** /v1/messages/{message_endpoint_id} | Update a messaging endpoint
[**update_message_endpoint**](MessagesApi.md#update_message_endpoint) | **POST** /v1/messages/register/{user_id} | Register a messaging endpoint on a user.


# **bulk_delete_messages**
> MessagesBulkDeleteResponse bulk_delete_messages(messages_bulk_delete_request)

Delete a list of messages and inbox items asociated to it.

Delete a list of messages and all associated inbox items. You can only delete so many messages in one request, to avoid long-running tasks that can never complete. To ensure all requests are deleted, iterate until the returned number of deleted messages is 0. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.messages_bulk_delete_response import MessagesBulkDeleteResponse
from agilicus_api.model.messages_bulk_delete_request import MessagesBulkDeleteRequest
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
    api_instance = messages_api.MessagesApi(api_client)
    messages_bulk_delete_request = MessagesBulkDeleteRequest(
        message_tag=MessageTag(
            tag_name=MessageTagName("reqID"),
            org_id="123",
        ),
        limit=5000,
        delete_expired=True,
    ) # MessagesBulkDeleteRequest | The object that describes the message(s) to delete

    # example passing only required values which don't have defaults set
    try:
        # Delete a list of messages and inbox items asociated to it.
        api_response = api_instance.bulk_delete_messages(messages_bulk_delete_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->bulk_delete_messages: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **messages_bulk_delete_request** | [**MessagesBulkDeleteRequest**](MessagesBulkDeleteRequest.md)| The object that describes the message(s) to delete |

### Return type

[**MessagesBulkDeleteResponse**](MessagesBulkDeleteResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | messages have been deleted |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_message**
> Message create_message(message_endpoint_id, message)

Send a message to a specific message endpoint.

Send a message to a specific message endpoint.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.message import Message
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
    api_instance = messages_api.MessagesApi(api_client)
    message_endpoint_id = "1234" # str | send a message on a message endpoint
    message = Message(
        title="title_example",
        sub_header="sub_header_example",
        icon="icon_example",
        image="image_example",
        text="text_example",
        uri="uri_example",
        context="context_example",
        actions=[
            MessageAction(
                title="title_example",
                uri="uri_example",
                icon="icon_example",
            ),
        ],
        message_type=MessageType("user-role-request"),
        message_class=MessageClass("admin-portal"),
        expiry_date=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
        tag=MessageTag(
            tag_name=MessageTagName("reqID"),
            org_id="123",
        ),
        push_probability=0.0205,
    ) # Message | Message

    # example passing only required values which don't have defaults set
    try:
        # Send a message to a specific message endpoint.
        api_response = api_instance.create_message(message_endpoint_id, message)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->create_message: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message_endpoint_id** | **str**| send a message on a message endpoint |
 **message** | [**Message**](Message.md)| Message |

### Return type

[**Message**](Message.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Return the message with uuid filled in |  -  |
**404** | User not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_routed_message**
> MessageSendResponse create_routed_message(message_send_request)

Send one or more messages, letting the system choose how to deliver it

Send one or more messages, leting the system choose to which endpoints to send it, based on properties of the message and the user's configuration. Each message can be associated with multiple addresses, each of which target a user. Note that some users, such as a group, may represent multiple recipients, in which case the message will be sent to users represented by the addressed user. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.message_send_request import MessageSendRequest
from agilicus_api.model.message_send_response import MessageSendResponse
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
    api_instance = messages_api.MessagesApi(api_client)
    message_send_request = MessageSendRequest(
        messages=[
            MessageSendItem(
                message=Message(
                    title="title_example",
                    sub_header="sub_header_example",
                    icon="icon_example",
                    image="image_example",
                    text="text_example",
                    uri="uri_example",
                    context="context_example",
                    actions=[
                        MessageAction(
                            title="title_example",
                            uri="uri_example",
                            icon="icon_example",
                        ),
                    ],
                    message_type=MessageType("user-role-request"),
                    message_class=MessageClass("admin-portal"),
                    expiry_date=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
                    tag=MessageTag(
                        tag_name=MessageTagName("reqID"),
                        org_id="123",
                    ),
                    push_probability=0.0205,
                ),
                addresses=[
                    MessageAddress(
                        user_id="123",
                        org_id="123",
                        direct=False,
                    ),
                ],
                ephemeral=False,
                endpoint_types=[
                    MessageEndpointType("web_push"),
                ],
            ),
        ],
    ) # MessageSendRequest | the request to send a message

    # example passing only required values which don't have defaults set
    try:
        # Send one or more messages, letting the system choose how to deliver it
        api_response = api_instance.create_routed_message(message_send_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->create_routed_message: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message_send_request** | [**MessageSendRequest**](MessageSendRequest.md)| the request to send a message |

### Return type

[**MessageSendResponse**](MessageSendResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Return the message with uuid filled in |  -  |
**404** | User not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_user_message**
> Message create_user_message(user_id, message)

Send a message to a user on all (optionally of a type) endpoints.

Send a message to a user on all (optionally of a type) endpoints.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.message import Message
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.message_endpoint_type import MessageEndpointType
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
    api_instance = messages_api.MessagesApi(api_client)
    user_id = "1234" # str | user_id path
    message = Message(
        title="title_example",
        sub_header="sub_header_example",
        icon="icon_example",
        image="image_example",
        text="text_example",
        uri="uri_example",
        context="context_example",
        actions=[
            MessageAction(
                title="title_example",
                uri="uri_example",
                icon="icon_example",
            ),
        ],
        message_type=MessageType("user-role-request"),
        message_class=MessageClass("admin-portal"),
        expiry_date=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
        tag=MessageTag(
            tag_name=MessageTagName("reqID"),
            org_id="123",
        ),
        push_probability=0.0205,
    ) # Message | Message
    message_endpoint_type = MessageEndpointType("sms") # MessageEndpointType | messaging endpoint type (optional)
    address = "15555555555" # str | messaging address (direct) (optional)

    # example passing only required values which don't have defaults set
    try:
        # Send a message to a user on all (optionally of a type) endpoints.
        api_response = api_instance.create_user_message(user_id, message)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->create_user_message: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Send a message to a user on all (optionally of a type) endpoints.
        api_response = api_instance.create_user_message(user_id, message, message_endpoint_type=message_endpoint_type, address=address)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->create_user_message: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| user_id path |
 **message** | [**Message**](Message.md)| Message |
 **message_endpoint_type** | **MessageEndpointType**| messaging endpoint type | [optional]
 **address** | **str**| messaging address (direct) | [optional]

### Return type

[**Message**](Message.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Return the message with uuid filled in |  -  |
**404** | User not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_inbox_item**
> delete_inbox_item(user_id, inbox_item_id)

Delete an inbox item

Delete a specific inbox item

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
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
    api_instance = messages_api.MessagesApi(api_client)
    user_id = "1234" # str | user_id path
    inbox_item_id = "P7UlkI49" # str | The id of the inbox item with which to interact 

    # example passing only required values which don't have defaults set
    try:
        # Delete an inbox item
        api_instance.delete_inbox_item(user_id, inbox_item_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->delete_inbox_item: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| user_id path |
 **inbox_item_id** | **str**| The id of the inbox item with which to interact  |

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
**204** | inbox item deleted |  -  |
**404** | inbox item not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_message_endpoint**
> delete_message_endpoint(message_endpoint_id)

Delete a messaging endpoint

Delete a messaging endpoint

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
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
    api_instance = messages_api.MessagesApi(api_client)
    message_endpoint_id = "1234" # str | messaging endpoint id
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a messaging endpoint
        api_instance.delete_message_endpoint(message_endpoint_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->delete_message_endpoint: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a messaging endpoint
        api_instance.delete_message_endpoint(message_endpoint_id, user_id=user_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->delete_message_endpoint: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message_endpoint_id** | **str**| messaging endpoint id |
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
**204** | Messaging endpoint deleted |  -  |
**404** | Messaging endpoint not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_inbox_item**
> InboxItem get_inbox_item(user_id, inbox_item_id)

Get an inbox item

Get a specific inbox item

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.inbox_item import InboxItem
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
    api_instance = messages_api.MessagesApi(api_client)
    user_id = "1234" # str | user_id path
    inbox_item_id = "P7UlkI49" # str | The id of the inbox item with which to interact 

    # example passing only required values which don't have defaults set
    try:
        # Get an inbox item
        api_response = api_instance.get_inbox_item(user_id, inbox_item_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->get_inbox_item: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| user_id path |
 **inbox_item_id** | **str**| The id of the inbox item with which to interact  |

### Return type

[**InboxItem**](InboxItem.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | return inbox item |  -  |
**404** | inbox item not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_message_endpoint**
> MessageEndpoint get_message_endpoint(message_endpoint_id)

Get a message endpoint

Get a message endpoint

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.message_endpoint import MessageEndpoint
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
    api_instance = messages_api.MessagesApi(api_client)
    message_endpoint_id = "1234" # str | messaging endpoint id
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a message endpoint
        api_response = api_instance.get_message_endpoint(message_endpoint_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->get_message_endpoint: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a message endpoint
        api_response = api_instance.get_message_endpoint(message_endpoint_id, user_id=user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->get_message_endpoint: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message_endpoint_id** | **str**| messaging endpoint id |
 **user_id** | **str**| Query based on user id | [optional]

### Return type

[**MessageEndpoint**](MessageEndpoint.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the detail of the message endpoint |  -  |
**404** | Messaging endpoint not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_inbox_items**
> ListInboxItemsResponse list_inbox_items(user_id)

Get a list of inbox items items and information about the inbox

Get a list of inbox items and information about the inbox for a user. By default only shows unexpired items. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.message_tag import MessageTag
from agilicus_api.model.list_inbox_items_response import ListInboxItemsResponse
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
    api_instance = messages_api.MessagesApi(api_client)
    user_id = "1234" # str | user_id path
    org_id = "1234" # str | Organisation Unique identifier (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    message_type = "message_type_example" # str | optional argument for restricting returned inbox items to only those of a specific type (optional)
    message_class = "message_class_example" # str | optional argument for restricting returned inbox items to only those of a specific class (optional)
    message_class_list = [
        "admin-portal",
    ] # [str] | optional argument for restricting returned inbox items to only those of a list of specific classes (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    page_at_received_date = dateutil_parser('2015-07-07T15:49:51.230+02:00') # datetime, none_type | Pagination based query with the date as the key. To get the initial entries supply null.  (optional)
    unread = True # bool | Search for items that have or have not been read.  (optional)
    expired = True # bool | Search for items that have or have not expired.  (optional)
    tag = MessageTag(
        tag_name=MessageTagName("reqID"),
        org_id="123",
    ) # MessageTag | Search messages based on tag (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a list of inbox items items and information about the inbox
        api_response = api_instance.list_inbox_items(user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->list_inbox_items: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a list of inbox items items and information about the inbox
        api_response = api_instance.list_inbox_items(user_id, org_id=org_id, limit=limit, message_type=message_type, message_class=message_class, message_class_list=message_class_list, page_at_id=page_at_id, page_at_received_date=page_at_received_date, unread=unread, expired=expired, tag=tag)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->list_inbox_items: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| user_id path |
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **message_type** | **str**| optional argument for restricting returned inbox items to only those of a specific type | [optional]
 **message_class** | **str**| optional argument for restricting returned inbox items to only those of a specific class | [optional]
 **message_class_list** | **[str]**| optional argument for restricting returned inbox items to only those of a list of specific classes | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **page_at_received_date** | **datetime, none_type**| Pagination based query with the date as the key. To get the initial entries supply null.  | [optional]
 **unread** | **bool**| Search for items that have or have not been read.  | [optional]
 **expired** | **bool**| Search for items that have or have not expired.  | [optional]
 **tag** | **MessageTag**| Search messages based on tag | [optional]

### Return type

[**ListInboxItemsResponse**](ListInboxItemsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return matching inbox items |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_message_endpoints**
> ListMessageEndpointsResponse list_message_endpoints()

List all message endpoints (all users or a single user)

List all message endpoints (all users or a single user)

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.list_message_endpoints_response import ListMessageEndpointsResponse
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
    api_instance = messages_api.MessagesApi(api_client)
    user_id = "1234" # str | Query based on user id (optional)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all message endpoints (all users or a single user)
        api_response = api_instance.list_message_endpoints(user_id=user_id, limit=limit)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->list_message_endpoints: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| Query based on user id | [optional]
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500

### Return type

[**ListMessageEndpointsResponse**](ListMessageEndpointsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of all message endpoints (for all users if user_id not present) |  -  |
**404** | No messaging endpoints exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_messages_config**
> MessageEndpointsConfig list_messages_config()

Get the config of the endpoint-types (e.g. public keys etc).

Get the config of the endpoint-types (e.g. public keys etc).

### Example

```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.message_endpoints_config import MessageEndpointsConfig
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = messages_api.MessagesApi(api_client)

    # example, this endpoint has no required or optional parameters
    try:
        # Get the config of the endpoint-types (e.g. public keys etc).
        api_response = api_instance.list_messages_config()
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->list_messages_config: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

[**MessageEndpointsConfig**](MessageEndpointsConfig.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the configuration of the messaging types (e.g. public keys etc). |  -  |
**404** | No messaging endpoints registered. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_inbox_item**
> InboxItem replace_inbox_item(user_id, inbox_item_id, inbox_item)

replace an inbox item

update an inbox item's writeable attributes

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.inbox_item import InboxItem
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
    api_instance = messages_api.MessagesApi(api_client)
    user_id = "1234" # str | user_id path
    inbox_item_id = "P7UlkI49" # str | The id of the inbox item with which to interact 
    inbox_item = InboxItem(
        metadata=InboxItemMetadata(
        ),
        spec=InboxItemSpec(
            has_been_read=True,
        ),
        status=InboxItemStatus(
            message=Message(
                title="title_example",
                sub_header="sub_header_example",
                icon="icon_example",
                image="image_example",
                text="text_example",
                uri="uri_example",
                context="context_example",
                actions=[
                    MessageAction(
                        title="title_example",
                        uri="uri_example",
                        icon="icon_example",
                    ),
                ],
                message_type=MessageType("user-role-request"),
                message_class=MessageClass("admin-portal"),
                expiry_date=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
                tag=MessageTag(
                    tag_name=MessageTagName("reqID"),
                    org_id="123",
                ),
                push_probability=0.0205,
            ),
            expired=False,
        ),
    ) # InboxItem | the inbox item to update

    # example passing only required values which don't have defaults set
    try:
        # replace an inbox item
        api_response = api_instance.replace_inbox_item(user_id, inbox_item_id, inbox_item)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->replace_inbox_item: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| user_id path |
 **inbox_item_id** | **str**| The id of the inbox item with which to interact  |
 **inbox_item** | [**InboxItem**](InboxItem.md)| the inbox item to update |

### Return type

[**InboxItem**](InboxItem.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | inbox item updated |  -  |
**400** | request was invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_message_endpoint**
> MessageEndpoint replace_message_endpoint(message_endpoint_id, message_endpoint)

Update a messaging endpoint

Update a messaging endpoint

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.message_endpoint import MessageEndpoint
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
    api_instance = messages_api.MessagesApi(api_client)
    message_endpoint_id = "1234" # str | messaging endpoint id
    message_endpoint = MessageEndpoint(
        metadata=MessageEndpointMetadata(
        ),
        spec=MessageEndpointSpec(
            endpoint_type=MessageEndpointType("web_push"),
            nickname="nickname_example",
            address="address_example",
            enabled=True,
        ),
    ) # MessageEndpoint | Message
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update a messaging endpoint
        api_response = api_instance.replace_message_endpoint(message_endpoint_id, message_endpoint)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->replace_message_endpoint: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a messaging endpoint
        api_response = api_instance.replace_message_endpoint(message_endpoint_id, message_endpoint, user_id=user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->replace_message_endpoint: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message_endpoint_id** | **str**| messaging endpoint id |
 **message_endpoint** | [**MessageEndpoint**](MessageEndpoint.md)| Message |
 **user_id** | **str**| Query based on user id | [optional]

### Return type

[**MessageEndpoint**](MessageEndpoint.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully updated messaging endpoint |  -  |
**404** | Messaging endpoint not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_message_endpoint**
> MessageEndpoint update_message_endpoint(user_id, message_endpoint)

Register a messaging endpoint on a user.

Register a messaging endpoint on a user.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import messages_api
from agilicus_api.model.message_endpoint import MessageEndpoint
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
    api_instance = messages_api.MessagesApi(api_client)
    user_id = "1234" # str | user_id path
    message_endpoint = MessageEndpoint(
        metadata=MessageEndpointMetadata(
        ),
        spec=MessageEndpointSpec(
            endpoint_type=MessageEndpointType("web_push"),
            nickname="nickname_example",
            address="address_example",
            enabled=True,
        ),
    ) # MessageEndpoint | Message

    # example passing only required values which don't have defaults set
    try:
        # Register a messaging endpoint on a user.
        api_response = api_instance.update_message_endpoint(user_id, message_endpoint)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling MessagesApi->update_message_endpoint: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**| user_id path |
 **message_endpoint** | [**MessageEndpoint**](MessageEndpoint.md)| Message |

### Return type

[**MessageEndpoint**](MessageEndpoint.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created messaging endpoint |  -  |
**409** | Duplicate address for this user |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

