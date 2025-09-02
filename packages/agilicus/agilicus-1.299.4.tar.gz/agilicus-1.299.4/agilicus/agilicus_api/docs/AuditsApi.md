# agilicus_api.AuditsApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_create_events**](AuditsApi.md#bulk_create_events) | **POST** /v1/bulk_audit_events | Process an AuditWebhookBulkEvent
[**create_audit_destination**](AuditsApi.md#create_audit_destination) | **POST** /v1/audit_destinations | Create an AuditDestination
[**delete_audit_destination**](AuditsApi.md#delete_audit_destination) | **DELETE** /v1/audit_destinations/{destination_id} | Remove an AuditDestination
[**get_audit_destination**](AuditsApi.md#get_audit_destination) | **GET** /v1/audit_destinations/{destination_id} | Get a single AuditDestination
[**list_audit_destinations**](AuditsApi.md#list_audit_destinations) | **GET** /v1/audit_destinations | View audit destinations
[**list_audits**](AuditsApi.md#list_audits) | **GET** /v1/audits | View audit records
[**list_auth_records**](AuditsApi.md#list_auth_records) | **GET** /v1/auth_audits | View authentication audit records
[**replace_audit_destination**](AuditsApi.md#replace_audit_destination) | **PUT** /v1/audit_destinations/{destination_id} | Create or update a AuditDestination.


# **bulk_create_events**
> AuditWebhookEventsProcessed bulk_create_events(audit_webhook_bulk_event)

Process an AuditWebhookBulkEvent

Processes an AuditWebhookBulkEvent by putting it into the audit event pipeline. Agilicus audit agents expect webhook destinations to obey the semantics of this API, though the URL at which to post AuditWebhookEvents may differ from this. That is, this API specification may be used to develop your own webhook for processing events. If the webhook wants to implement fine-grained processing of events, it should respond with the AuditWebhookEventProcessed response. Otherwise, the audit agent should assume that the response applies to all entries. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import audits_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.audit_webhook_events_processed import AuditWebhookEventsProcessed
from agilicus_api.model.audit_webhook_bulk_event import AuditWebhookBulkEvent
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
    api_instance = audits_api.AuditsApi(api_client)
    audit_webhook_bulk_event = AuditWebhookBulkEvent(
        events=[
            AuditEvent(
                unique_id="2",
                create_time=dateutil_parser('1970-01-01T00:00:00.00Z'),
                event={},
            ),
        ],
        always_respond_with_events=True,
    ) # AuditWebhookBulkEvent | 

    # example passing only required values which don't have defaults set
    try:
        # Process an AuditWebhookBulkEvent
        api_response = api_instance.bulk_create_events(audit_webhook_bulk_event)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->bulk_create_events: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audit_webhook_bulk_event** | [**AuditWebhookBulkEvent**](AuditWebhookBulkEvent.md)|  |

### Return type

[**AuditWebhookEventsProcessed**](AuditWebhookEventsProcessed.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | The AuditWebhookEvents were processed. See the AuditWebhookEventProcessed response for how each event was processed, because some may have failed. Note that if this returns nothing in its response, the caller should assume that all events were properly processed.  |  -  |
**400** | The AuditWebhookBulkEvent was malformed. It should be discarded.  |  -  |
**429** | The system is too busy. Try again later. See the &#x60;Retry-After&#x60; header for a suggested time at which to try again.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_audit_destination**
> AuditDestination create_audit_destination(audit_destination)

Create an AuditDestination

Creating a new AuditDestination allows administrators to connect their sources of audit events to somewhere they can be stored. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import audits_api
from agilicus_api.model.audit_destination import AuditDestination
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
    api_instance = audits_api.AuditsApi(api_client)
    audit_destination = AuditDestination(
        metadata=MetadataWithId(),
        spec=AuditDestinationSpec(
            enabled=True,
            name="access-logs-file",
            org_id="123",
            destination_type="file",
            location="file://./audits.log",
            max_events_per_transaction=500,
            comment="Tracks access logs. Backed up daily.",
            filters=[
                AuditDestinationFilter(
                    filter_type="subsystem",
                    value="access",
                    or_list=[
                        "access",
                    ],
                ),
            ],
            authentication=AuditDestinationAuthentication(
                authentication_type="agilicus_bearer",
                http_basic=HTTPBasicAuth(
                    username="me@example.com",
                    password="_+\Sj4x!N$qFW5Umv",
                ),
                http_bearer=HTTPBearerAuth(
                    token="aGVsbG8gd29ybGQgbXkgdG9rZW4gaXMgY29vbAo=",
                ),
            ),
        ),
    ) # AuditDestination | 

    # example passing only required values which don't have defaults set
    try:
        # Create an AuditDestination
        api_response = api_instance.create_audit_destination(audit_destination)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->create_audit_destination: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audit_destination** | [**AuditDestination**](AuditDestination.md)|  |

### Return type

[**AuditDestination**](AuditDestination.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New AuditDestination created |  -  |
**409** | An AuditDestination with the same name already exists for this organisation. The existing AuditDestination is returned.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_audit_destination**
> delete_audit_destination(destination_id)

Remove an AuditDestination

Remove an AuditDestination. After removal, the system will stop sending events to the destination. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import audits_api
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
    api_instance = audits_api.AuditsApi(api_client)
    destination_id = "1234" # str | destinaton id in path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Remove an AuditDestination
        api_instance.delete_audit_destination(destination_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->delete_audit_destination: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Remove an AuditDestination
        api_instance.delete_audit_destination(destination_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->delete_audit_destination: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_id** | **str**| destinaton id in path |
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
**204** | AuditDestination was deleted |  -  |
**404** | AuditDestination does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_audit_destination**
> AuditDestination get_audit_destination(destination_id)

Get a single AuditDestination

Get the details of a single AuditDestination. Specify the id of the organisation which owns this resource to ensure you have permission. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import audits_api
from agilicus_api.model.audit_destination import AuditDestination
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
    api_instance = audits_api.AuditsApi(api_client)
    destination_id = "1234" # str | destinaton id in path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a single AuditDestination
        api_response = api_instance.get_audit_destination(destination_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->get_audit_destination: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a single AuditDestination
        api_response = api_instance.get_audit_destination(destination_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->get_audit_destination: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_id** | **str**| destinaton id in path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**AuditDestination**](AuditDestination.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The AuditDestination was found. |  -  |
**404** | The AuditDestination does not exist. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_audit_destinations**
> ListAuditDestinationsResponse list_audit_destinations()

View audit destinations

View configured audit destinations

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import audits_api
from agilicus_api.model.list_audit_destinations_response import ListAuditDestinationsResponse
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
    api_instance = audits_api.AuditsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    destination_type = "1234" # str | Destinaton_type in query. Filters AuditDestinations based on their type.  (optional)
    name = "name-1" # str | Filters based on whether or not the items in the collection have the given name.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # View audit destinations
        api_response = api_instance.list_audit_destinations(limit=limit, org_id=org_id, destination_type=destination_type, name=name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->list_audit_destinations: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **destination_type** | **str**| Destinaton_type in query. Filters AuditDestinations based on their type.  | [optional]
 **name** | **str**| Filters based on whether or not the items in the collection have the given name.  | [optional]

### Return type

[**ListAuditDestinationsResponse**](ListAuditDestinationsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The query ran without error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_audits**
> ListAuditsResponse list_audits()

View audit records

View audit records for any API.  The attribute_type, attribute_id and attribute_org_id query provides the ability to query attributes for an audit record across all possible attributes thay maybe associated with a record, as audit records may have multiple multiple attributes (AuditAttribute) per record. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import audits_api
from agilicus_api.model.list_audits_response import ListAuditsResponse
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
    api_instance = audits_api.AuditsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    user_id = "1234" # str | Query based on user id (optional)
    dt_from = "" # str | Search criteria from when the query happened. * Inclusive. * In UTC. * Supports human-friendly values such as \"now\", \"today\", \"now-1day\".  (optional) if omitted the server will use the default value of ""
    dt_to = "" # str | Search criteria until when the query happened. * Exclusive. * In UTC. * Supports human-friendly values such as \"now\", \"today\", \"now-1day\".  (optional) if omitted the server will use the default value of ""
    action = "" # str | the type of action which caused the log (optional) if omitted the server will use the default value of ""
    target_id = "" # str | The identifier for the target of the log (e.g. the jti of a created token).  (optional) if omitted the server will use the default value of ""
    token_id = "123" # str | The id of the bearer token for which to find records. (optional)
    api_name = "" # str | The name of the API which generated the audit logs (optional) if omitted the server will use the default value of ""
    target_resource_type = "" # str | Filters the type of resource associated with the audit records. (optional) if omitted the server will use the default value of ""
    org_id = "1234" # str | Organisation Unique identifier (optional)
    attribute_type = "attribute_type_example" # str | Filters the attribute_type associated with an audit record. (optional)
    attribute_id = "attribute_id_example" # str | Filters the attribute_id associated with an audit record. (optional)
    attribute_org_id = "attribute_org_id_example" # str | Filters the attribute_org_id associated with an audit record. (optional)
    resources_behind_connector_id = "1234" # str | search audit records for all resources behind a connector (optional)
    attribute_type_list = [
        "attribute_type_list_example",
    ] # [str] | a list of attribute_types for searching audit records. (optional)
    attribute_id_list = [
        "attribute_id_list_example",
    ] # [str] | a list of attribute_ids for searching audit records. (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # View audit records
        api_response = api_instance.list_audits(limit=limit, user_id=user_id, dt_from=dt_from, dt_to=dt_to, action=action, target_id=target_id, token_id=token_id, api_name=api_name, target_resource_type=target_resource_type, org_id=org_id, attribute_type=attribute_type, attribute_id=attribute_id, attribute_org_id=attribute_org_id, resources_behind_connector_id=resources_behind_connector_id, attribute_type_list=attribute_type_list, attribute_id_list=attribute_id_list)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->list_audits: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **user_id** | **str**| Query based on user id | [optional]
 **dt_from** | **str**| Search criteria from when the query happened. * Inclusive. * In UTC. * Supports human-friendly values such as \&quot;now\&quot;, \&quot;today\&quot;, \&quot;now-1day\&quot;.  | [optional] if omitted the server will use the default value of ""
 **dt_to** | **str**| Search criteria until when the query happened. * Exclusive. * In UTC. * Supports human-friendly values such as \&quot;now\&quot;, \&quot;today\&quot;, \&quot;now-1day\&quot;.  | [optional] if omitted the server will use the default value of ""
 **action** | **str**| the type of action which caused the log | [optional] if omitted the server will use the default value of ""
 **target_id** | **str**| The identifier for the target of the log (e.g. the jti of a created token).  | [optional] if omitted the server will use the default value of ""
 **token_id** | **str**| The id of the bearer token for which to find records. | [optional]
 **api_name** | **str**| The name of the API which generated the audit logs | [optional] if omitted the server will use the default value of ""
 **target_resource_type** | **str**| Filters the type of resource associated with the audit records. | [optional] if omitted the server will use the default value of ""
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **attribute_type** | **str**| Filters the attribute_type associated with an audit record. | [optional]
 **attribute_id** | **str**| Filters the attribute_id associated with an audit record. | [optional]
 **attribute_org_id** | **str**| Filters the attribute_org_id associated with an audit record. | [optional]
 **resources_behind_connector_id** | **str**| search audit records for all resources behind a connector | [optional]
 **attribute_type_list** | **[str]**| a list of attribute_types for searching audit records. | [optional]
 **attribute_id_list** | **[str]**| a list of attribute_ids for searching audit records. | [optional]

### Return type

[**ListAuditsResponse**](ListAuditsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The query ran without error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_auth_records**
> ListAuthAuditsResponse list_auth_records()

View authentication audit records

View and search authentication audit records for different users and organisations in the system. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import audits_api
from agilicus_api.model.list_auth_audits_response import ListAuthAuditsResponse
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
    api_instance = audits_api.AuditsApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    user_id = "1234" # str | Query based on user id (optional)
    dt_from = "" # str | Search criteria from when the query happened. * Inclusive. * In UTC. * Supports human-friendly values such as \"now\", \"today\", \"now-1day\".  (optional) if omitted the server will use the default value of ""
    dt_to = "" # str | Search criteria until when the query happened. * Exclusive. * In UTC. * Supports human-friendly values such as \"now\", \"today\", \"now-1day\".  (optional) if omitted the server will use the default value of ""
    org_id = "1234" # str | Organisation Unique identifier (optional)
    session_id = "1234" # str | The session formed when the user started to log in. (optional)
    trace_id = "1234-abcd" # str | The id representing the request that triggered the event (optional)
    upstream_user_id = "1234-abcd" # str | The id of the user from upstream (optional)
    upstream_idp = "google" # str | The name of the upstream idp (optional)
    login_org_id = "1234" # str | The org id the user tried to log in to (optional)
    source_ip = "192.0.2.3" # str | The source IP address of the client device logging in. (optional)
    client_id = "my-client-123" # str | The oidc client id used to log in (optional)
    event = "Success" # str | The event which triggered the audit record (optional)
    stage = "Login" # str | The stage of a pipeline to query for (optional)
    request_id = "abcd-1234-efgh" # str | The request id associated with an audit record  (optional)
    result = "Success" # str | The result of an authentication audit to query. (optional)
    event_name = "Authentication Request" # str | query the event_name in authentication audit (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # View authentication audit records
        api_response = api_instance.list_auth_records(limit=limit, user_id=user_id, dt_from=dt_from, dt_to=dt_to, org_id=org_id, session_id=session_id, trace_id=trace_id, upstream_user_id=upstream_user_id, upstream_idp=upstream_idp, login_org_id=login_org_id, source_ip=source_ip, client_id=client_id, event=event, stage=stage, request_id=request_id, result=result, event_name=event_name)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->list_auth_records: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **user_id** | **str**| Query based on user id | [optional]
 **dt_from** | **str**| Search criteria from when the query happened. * Inclusive. * In UTC. * Supports human-friendly values such as \&quot;now\&quot;, \&quot;today\&quot;, \&quot;now-1day\&quot;.  | [optional] if omitted the server will use the default value of ""
 **dt_to** | **str**| Search criteria until when the query happened. * Exclusive. * In UTC. * Supports human-friendly values such as \&quot;now\&quot;, \&quot;today\&quot;, \&quot;now-1day\&quot;.  | [optional] if omitted the server will use the default value of ""
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **session_id** | **str**| The session formed when the user started to log in. | [optional]
 **trace_id** | **str**| The id representing the request that triggered the event | [optional]
 **upstream_user_id** | **str**| The id of the user from upstream | [optional]
 **upstream_idp** | **str**| The name of the upstream idp | [optional]
 **login_org_id** | **str**| The org id the user tried to log in to | [optional]
 **source_ip** | **str**| The source IP address of the client device logging in. | [optional]
 **client_id** | **str**| The oidc client id used to log in | [optional]
 **event** | **str**| The event which triggered the audit record | [optional]
 **stage** | **str**| The stage of a pipeline to query for | [optional]
 **request_id** | **str**| The request id associated with an audit record  | [optional]
 **result** | **str**| The result of an authentication audit to query. | [optional]
 **event_name** | **str**| query the event_name in authentication audit | [optional]

### Return type

[**ListAuthAuditsResponse**](ListAuthAuditsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The query ran without error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_audit_destination**
> AuditDestination replace_audit_destination(destination_id)

Create or update a AuditDestination.

Create or update a AuditDestination.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import audits_api
from agilicus_api.model.audit_destination import AuditDestination
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
    api_instance = audits_api.AuditsApi(api_client)
    destination_id = "1234" # str | destinaton id in path
    audit_destination = AuditDestination(
        metadata=MetadataWithId(),
        spec=AuditDestinationSpec(
            enabled=True,
            name="access-logs-file",
            org_id="123",
            destination_type="file",
            location="file://./audits.log",
            max_events_per_transaction=500,
            comment="Tracks access logs. Backed up daily.",
            filters=[
                AuditDestinationFilter(
                    filter_type="subsystem",
                    value="access",
                    or_list=[
                        "access",
                    ],
                ),
            ],
            authentication=AuditDestinationAuthentication(
                authentication_type="agilicus_bearer",
                http_basic=HTTPBasicAuth(
                    username="me@example.com",
                    password="_+\Sj4x!N$qFW5Umv",
                ),
                http_bearer=HTTPBearerAuth(
                    token="aGVsbG8gd29ybGQgbXkgdG9rZW4gaXMgY29vbAo=",
                ),
            ),
        ),
    ) # AuditDestination |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Create or update a AuditDestination.
        api_response = api_instance.replace_audit_destination(destination_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->replace_audit_destination: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Create or update a AuditDestination.
        api_response = api_instance.replace_audit_destination(destination_id, audit_destination=audit_destination)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling AuditsApi->replace_audit_destination: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **destination_id** | **str**| destinaton id in path |
 **audit_destination** | [**AuditDestination**](AuditDestination.md)|  | [optional]

### Return type

[**AuditDestination**](AuditDestination.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The AuditDestination was updated. Returns the latest version of it after the update was applied.  |  -  |
**404** | AuditDestination does not exist. |  -  |
**409** | The provided AuditDestination conflicted with the value stored in the API. Please fetch the latest version and try again with it.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

