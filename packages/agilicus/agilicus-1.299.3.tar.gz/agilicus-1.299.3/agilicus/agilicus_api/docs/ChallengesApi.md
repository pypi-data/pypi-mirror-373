# agilicus_api.ChallengesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_challenge**](ChallengesApi.md#create_challenge) | **POST** /v1/challenges | create a challenge
[**create_one_time_use_action**](ChallengesApi.md#create_one_time_use_action) | **POST** /v1/challenges/one_time_use_actions | create a one time use action challenge
[**create_totp_enrollment**](ChallengesApi.md#create_totp_enrollment) | **POST** /v1/challenge_enrollment/totp | create a TOTP challenge enrollment
[**create_webauthn_enrollment**](ChallengesApi.md#create_webauthn_enrollment) | **POST** /v1/challenge_enrollment/webauthn | create a WebAuthN challenge enrollment
[**delete_challenge**](ChallengesApi.md#delete_challenge) | **DELETE** /v1/challenges/{challenge_id} | Delete the challenge specified by challenge_id
[**delete_totp_enrollment**](ChallengesApi.md#delete_totp_enrollment) | **DELETE** /v1/challenge_enrollment/totp/{totp_id} | Delete the TOTP enrollment specified by totp id
[**delete_webauthn_enrollment**](ChallengesApi.md#delete_webauthn_enrollment) | **DELETE** /v1/challenge_enrollment/webauthn/{webauthn_id} | Delete the WebAuthN enrollment specified by webauthn_id
[**get_answer**](ChallengesApi.md#get_answer) | **GET** /v1/challenges/{challenge_id}/answers | answer a challenge
[**get_challenge**](ChallengesApi.md#get_challenge) | **GET** /v1/challenges/{challenge_id} | Get the challenge specified by challenge_id
[**get_totp_enrollment**](ChallengesApi.md#get_totp_enrollment) | **GET** /v1/challenge_enrollment/totp/{totp_id} | Get the TOTP enrollment specified by totp_id
[**get_webauthn_enrollment**](ChallengesApi.md#get_webauthn_enrollment) | **GET** /v1/challenge_enrollment/webauthn/{webauthn_id} | Get the WebAuthN enrollment specified by webauthn_id
[**list_totp_enrollment**](ChallengesApi.md#list_totp_enrollment) | **GET** /v1/challenge_enrollment/totp | List the totp enrollment results
[**list_webauthn_enrollments**](ChallengesApi.md#list_webauthn_enrollments) | **GET** /v1/challenge_enrollment/webauthn | List the webauthn enrollments
[**replace_challenge**](ChallengesApi.md#replace_challenge) | **PUT** /v1/challenges/{challenge_id} | Replace the challenge specified by challenge_id
[**update_totp_enrollment**](ChallengesApi.md#update_totp_enrollment) | **POST** /v1/challenge_enrollment/totp/{totp_id} | Update the totp_enrollment if the answer provided is correct.
[**update_webauthn_enrollment**](ChallengesApi.md#update_webauthn_enrollment) | **POST** /v1/challenge_enrollment/webauthn/{webauthn_id} | Update the WebAuthN enrollment if the answer provided is correct.


# **create_challenge**
> Challenge create_challenge(challenge)

create a challenge

Creates a challenge according to the provide specification. This challenge will persist for a period of time waiting for the challenge to be passed. It will eventually time out. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.challenge import Challenge
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
    api_instance = challenges_api.ChallengesApi(api_client)
    challenge = Challenge(
        metadata=MetadataWithId(),
        spec=ChallengeSpec(
            challenge_type="challenge_type_example",
            challenge_types=[
                "challenge_types_example",
            ],
            send_now=False,
            timeout_seconds=600,
            response_uri="https://auth.egov.city/mfa-answer",
            origin="origin_example",
            challenge_endpoints=[
                ChallengeEndpoint(
                    endpoint="endpoint_example",
                    type="type_example",
                ),
            ],
            answer_data={},
        ),
        status=ChallengeStatus(
            state="issued",
            public_challenge="public_challenge_example",
            code="at4Bk6Aad39",
            answered_at=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
        ),
    ) # Challenge | The challenge to create

    # example passing only required values which don't have defaults set
    try:
        # create a challenge
        api_response = api_instance.create_challenge(challenge)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->create_challenge: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **challenge** | [**Challenge**](Challenge.md)| The challenge to create |

### Return type

[**Challenge**](Challenge.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created the challenge. Depending on whether &#x60;send_now&#x60; was true, it could be waiting for an answer.  |  -  |
**400** | Error creating challenge. See error message body for more details. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_one_time_use_action**
> OneTimeUseActionChallengeResponse create_one_time_use_action(one_time_use_action_challenge)

create a one time use action challenge

Creates a one time use challenge according to the provide specification. This challenge will persist for a period of time waiting for the challenge to be passed. It will eventually time out. If the challenge is accepted or declined, the system will perform an action according to the configuration provided on challenge creation and the provided answer. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.one_time_use_action_challenge_response import OneTimeUseActionChallengeResponse
from agilicus_api.model.one_time_use_action_challenge import OneTimeUseActionChallenge
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
    api_instance = challenges_api.ChallengesApi(api_client)
    one_time_use_action_challenge = OneTimeUseActionChallenge(
        spec=OneTimeUseActionChallengeSpec(
            user_id="123",
            org_id="123",
            approved_actions=[
                ChallengeAction(
                    challenge_action_type="HTTPChallengeAction",
                    method="GET",
                    body="/",
                    content_type="/",
                    uri="https://api.agilicus.com/v2/applications",
                    scopes=[
                        TokenScope("urn:agilicus:users:owner"),
                    ],
                ),
            ],
            declined_actions=[
                ChallengeAction(
                    challenge_action_type="HTTPChallengeAction",
                    method="GET",
                    body="/",
                    content_type="/",
                    uri="https://api.agilicus.com/v2/applications",
                    scopes=[
                        TokenScope("urn:agilicus:users:owner"),
                    ],
                ),
            ],
            actors=[
                ChallengeActor(
                    user_id="123",
                    org_id="123",
                ),
            ],
            timeout_seconds=1,
        ),
    ) # OneTimeUseActionChallenge | The challenge to create

    # example passing only required values which don't have defaults set
    try:
        # create a one time use action challenge
        api_response = api_instance.create_one_time_use_action(one_time_use_action_challenge)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->create_one_time_use_action: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **one_time_use_action_challenge** | [**OneTimeUseActionChallenge**](OneTimeUseActionChallenge.md)| The challenge to create |

### Return type

[**OneTimeUseActionChallengeResponse**](OneTimeUseActionChallengeResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created the challenge.  |  -  |
**400** | Error creating challenge. See error message body for more details. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_totp_enrollment**
> TOTPEnrollment create_totp_enrollment(totp_enrollment)

create a TOTP challenge enrollment

Creates a TOTP challenge enrollment. The returned body will contain the key the user needs to enroll in their application. The enrollment is not complete until the user provides a valid answer. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.totp_enrollment import TOTPEnrollment
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
    api_instance = challenges_api.ChallengesApi(api_client)
    totp_enrollment = TOTPEnrollment(
        metadata=MetadataWithId(),
        spec=TOTPEnrollmentSpec(
        ),
        status=TOTPEnrollmentStatus(
            state="pending",
            key="asdas43ADlaksda8739asfoafsalkasjd",
        ),
    ) # TOTPEnrollment | The TOTP challenge enrollment to create.

    # example passing only required values which don't have defaults set
    try:
        # create a TOTP challenge enrollment
        api_response = api_instance.create_totp_enrollment(totp_enrollment)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->create_totp_enrollment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **totp_enrollment** | [**TOTPEnrollment**](TOTPEnrollment.md)| The TOTP challenge enrollment to create. |

### Return type

[**TOTPEnrollment**](TOTPEnrollment.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created the TOTP challenge enrollment.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_webauthn_enrollment**
> WebAuthNEnrollment create_webauthn_enrollment(web_auth_n_enrollment)

create a WebAuthN challenge enrollment

Initiates a WebAuthN challenge enrollment. The enrollment is not complete until the user provides a valid answer. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.web_auth_n_enrollment import WebAuthNEnrollment
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
    api_instance = challenges_api.ChallengesApi(api_client)
    web_auth_n_enrollment = WebAuthNEnrollment(
        metadata=MetadataWithId(),
        spec=WebAuthNEnrollmentSpec(
            user_id="123",
            relying_party_id="123",
            attestation_format="platform",
            attestation_conveyance="direct",
            user_verification="discouraged",
            http_endpoint="https://webauthn.example.com/authenticate",
        ),
        status=WebAuthNEnrollmentStatus(
            challenge="asdas43ADlaksda8739asfoafsalkasjd",
            credential_id='YQ==',
            transports=[
                "ble",
            ],
        ),
    ) # WebAuthNEnrollment | The WebAuthN challenge enrollment to create.

    # example passing only required values which don't have defaults set
    try:
        # create a WebAuthN challenge enrollment
        api_response = api_instance.create_webauthn_enrollment(web_auth_n_enrollment)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->create_webauthn_enrollment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **web_auth_n_enrollment** | [**WebAuthNEnrollment**](WebAuthNEnrollment.md)| The WebAuthN challenge enrollment to create. |

### Return type

[**WebAuthNEnrollment**](WebAuthNEnrollment.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created the WebAuthN challenge enrollment.  |  -  |
**400** | Incorrect parameters supplied. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_challenge**
> delete_challenge(challenge_id)

Delete the challenge specified by challenge_id

Delete the challenge specified by challenge_id

### Example

```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = challenges_api.ChallengesApi(api_client)
    challenge_id = "AbasaWlLLS" # str | A challenge id found in a path.

    # example passing only required values which don't have defaults set
    try:
        # Delete the challenge specified by challenge_id
        api_instance.delete_challenge(challenge_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->delete_challenge: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **challenge_id** | **str**| A challenge id found in a path. |

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Challenge was deleted |  -  |
**404** | Challenge not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_totp_enrollment**
> delete_totp_enrollment(totp_id)

Delete the TOTP enrollment specified by totp id

Delete the TOTP enrollment specified by totp id

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
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
    api_instance = challenges_api.ChallengesApi(api_client)
    totp_id = "AbasaWlLLS" # str | A totp id found in a path.
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete the TOTP enrollment specified by totp id
        api_instance.delete_totp_enrollment(totp_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->delete_totp_enrollment: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete the TOTP enrollment specified by totp id
        api_instance.delete_totp_enrollment(totp_id, user_id=user_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->delete_totp_enrollment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **totp_id** | **str**| A totp id found in a path. |
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
**204** | Enrollment was deleted |  -  |
**404** | Enrollment not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_webauthn_enrollment**
> delete_webauthn_enrollment(webauthn_id)

Delete the WebAuthN enrollment specified by webauthn_id

Delete the WebAuthN enrollment specified by webauthn_id

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
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
    api_instance = challenges_api.ChallengesApi(api_client)
    webauthn_id = "AbasaWlLLS" # str | A webauthn id found in a path.
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete the WebAuthN enrollment specified by webauthn_id
        api_instance.delete_webauthn_enrollment(webauthn_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->delete_webauthn_enrollment: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete the WebAuthN enrollment specified by webauthn_id
        api_instance.delete_webauthn_enrollment(webauthn_id, user_id=user_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->delete_webauthn_enrollment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webauthn_id** | **str**| A webauthn id found in a path. |
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
**204** | Enrollment was deleted |  -  |
**404** | Enrollment not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_answer**
> ChallengeAnswer get_answer(challenge_id, challenge_answer, allowed, challenge_type)

answer a challenge

Checks whether the challenge answer is correct. If the challenge is not accepting answers, or the anwer is incorrect, a failure will be returned. Otherwise, the challenge will be considered answered and the user can log in. 

### Example

```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.challenge_answer import ChallengeAnswer
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = challenges_api.ChallengesApi(api_client)
    challenge_id = "AbasaWlLLS" # str | A challenge id found in a path.
    challenge_answer = "AbasaWlLLS" # str | The answer for the challenge
    allowed = False # bool | Whether the challenge was allowed. If true, then the user can proceed with the login. If false, then the user will be denied their login attempt. Set this to false if the login attempt was not desired. 
    challenge_type = "sms" # str | challenge method type query
    challenge_uid = "AbasaWlLLS" # str | The user id for the challenge (optional)

    # example passing only required values which don't have defaults set
    try:
        # answer a challenge
        api_response = api_instance.get_answer(challenge_id, challenge_answer, allowed, challenge_type)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->get_answer: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # answer a challenge
        api_response = api_instance.get_answer(challenge_id, challenge_answer, allowed, challenge_type, challenge_uid=challenge_uid)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->get_answer: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **challenge_id** | **str**| A challenge id found in a path. |
 **challenge_answer** | **str**| The answer for the challenge |
 **allowed** | **bool**| Whether the challenge was allowed. If true, then the user can proceed with the login. If false, then the user will be denied their login attempt. Set this to false if the login attempt was not desired.  |
 **challenge_type** | **str**| challenge method type query |
 **challenge_uid** | **str**| The user id for the challenge | [optional]

### Return type

[**ChallengeAnswer**](ChallengeAnswer.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successfully answered the challenge. The user may now proceed with their login. |  -  |
**400** | The challenge answer failed. No particular reason will be given. |  -  |
**404** | Challenge not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_challenge**
> Challenge get_challenge(challenge_id)

Get the challenge specified by challenge_id

Get the challenge specified by challenge_id

### Example

```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.challenge import Challenge
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = challenges_api.ChallengesApi(api_client)
    challenge_id = "AbasaWlLLS" # str | A challenge id found in a path.

    # example passing only required values which don't have defaults set
    try:
        # Get the challenge specified by challenge_id
        api_response = api_instance.get_challenge(challenge_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->get_challenge: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **challenge_id** | **str**| A challenge id found in a path. |

### Return type

[**Challenge**](Challenge.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the challenge by id |  -  |
**404** | Challenge not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_totp_enrollment**
> TOTPEnrollment get_totp_enrollment(totp_id)

Get the TOTP enrollment specified by totp_id

Get the TOTP enrollment specified by totp_id

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.totp_enrollment import TOTPEnrollment
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
    api_instance = challenges_api.ChallengesApi(api_client)
    totp_id = "AbasaWlLLS" # str | A totp id found in a path.
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get the TOTP enrollment specified by totp_id
        api_response = api_instance.get_totp_enrollment(totp_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->get_totp_enrollment: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get the TOTP enrollment specified by totp_id
        api_response = api_instance.get_totp_enrollment(totp_id, user_id=user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->get_totp_enrollment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **totp_id** | **str**| A totp id found in a path. |
 **user_id** | **str**| Query based on user id | [optional]

### Return type

[**TOTPEnrollment**](TOTPEnrollment.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the TOTP enrollment result by id |  -  |
**404** | Enrollment not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_webauthn_enrollment**
> WebAuthNEnrollment get_webauthn_enrollment(webauthn_id)

Get the WebAuthN enrollment specified by webauthn_id

Get the WebAuthN enrollment specified by webauthn_id

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.web_auth_n_enrollment import WebAuthNEnrollment
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
    api_instance = challenges_api.ChallengesApi(api_client)
    webauthn_id = "AbasaWlLLS" # str | A webauthn id found in a path.
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get the WebAuthN enrollment specified by webauthn_id
        api_response = api_instance.get_webauthn_enrollment(webauthn_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->get_webauthn_enrollment: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get the WebAuthN enrollment specified by webauthn_id
        api_response = api_instance.get_webauthn_enrollment(webauthn_id, user_id=user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->get_webauthn_enrollment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webauthn_id** | **str**| A webauthn id found in a path. |
 **user_id** | **str**| Query based on user id | [optional]

### Return type

[**WebAuthNEnrollment**](WebAuthNEnrollment.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the WebAuthN enrollment result by id |  -  |
**404** | Enrollment not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_totp_enrollment**
> ListTOTPEnrollmentResponse list_totp_enrollment()

List the totp enrollment results

List the totp enrollment results

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.list_totp_enrollment_response import ListTOTPEnrollmentResponse
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
    api_instance = challenges_api.ChallengesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List the totp enrollment results
        api_response = api_instance.list_totp_enrollment(limit=limit, user_id=user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->list_totp_enrollment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **user_id** | **str**| Query based on user id | [optional]

### Return type

[**ListTOTPEnrollmentResponse**](ListTOTPEnrollmentResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the TOTP enrollment results |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_webauthn_enrollments**
> ListWebAuthNEnrollmentResponse list_webauthn_enrollments()

List the webauthn enrollments

List the webauthn enrollments

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.list_web_auth_n_enrollment_response import ListWebAuthNEnrollmentResponse
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
    api_instance = challenges_api.ChallengesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List the webauthn enrollments
        api_response = api_instance.list_webauthn_enrollments(limit=limit, user_id=user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->list_webauthn_enrollments: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **user_id** | **str**| Query based on user id | [optional]

### Return type

[**ListWebAuthNEnrollmentResponse**](ListWebAuthNEnrollmentResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return the WebAuthN enrollment results |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_challenge**
> Challenge replace_challenge(challenge_id, challenge)

Replace the challenge specified by challenge_id

Replace the challenge specified by challenge_id

### Example

```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.challenge import Challenge
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = challenges_api.ChallengesApi(api_client)
    challenge_id = "AbasaWlLLS" # str | A challenge id found in a path.
    challenge = Challenge(
        metadata=MetadataWithId(),
        spec=ChallengeSpec(
            challenge_type="challenge_type_example",
            challenge_types=[
                "challenge_types_example",
            ],
            send_now=False,
            timeout_seconds=600,
            response_uri="https://auth.egov.city/mfa-answer",
            origin="origin_example",
            challenge_endpoints=[
                ChallengeEndpoint(
                    endpoint="endpoint_example",
                    type="type_example",
                ),
            ],
            answer_data={},
        ),
        status=ChallengeStatus(
            state="issued",
            public_challenge="public_challenge_example",
            code="at4Bk6Aad39",
            answered_at=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
        ),
    ) # Challenge | The challenge to replace. Note that some fields, such as user_id, cannot be modified.

    # example passing only required values which don't have defaults set
    try:
        # Replace the challenge specified by challenge_id
        api_response = api_instance.replace_challenge(challenge_id, challenge)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->replace_challenge: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **challenge_id** | **str**| A challenge id found in a path. |
 **challenge** | [**Challenge**](Challenge.md)| The challenge to replace. Note that some fields, such as user_id, cannot be modified. |

### Return type

[**Challenge**](Challenge.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The challenge was replaced. The result contains the updated challenge. |  -  |
**404** | Challenge not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_totp_enrollment**
> TOTPEnrollment update_totp_enrollment(totp_id, totp_enrollment_answer)

Update the totp_enrollment if the answer provided is correct.

Update the totp_enrollment if the answer provided is correct. This moves the state from pending to success.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.totp_enrollment import TOTPEnrollment
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.totp_enrollment_answer import TOTPEnrollmentAnswer
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
    api_instance = challenges_api.ChallengesApi(api_client)
    totp_id = "AbasaWlLLS" # str | A totp id found in a path.
    totp_enrollment_answer = TOTPEnrollmentAnswer(
        answer="asdas43ADlaksda8739asfoafsalkasjd",
    ) # TOTPEnrollmentAnswer | The answer to the TOTP enrollment specified by totp_id.
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update the totp_enrollment if the answer provided is correct.
        api_response = api_instance.update_totp_enrollment(totp_id, totp_enrollment_answer)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->update_totp_enrollment: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update the totp_enrollment if the answer provided is correct.
        api_response = api_instance.update_totp_enrollment(totp_id, totp_enrollment_answer, user_id=user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->update_totp_enrollment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **totp_id** | **str**| A totp id found in a path. |
 **totp_enrollment_answer** | [**TOTPEnrollmentAnswer**](TOTPEnrollmentAnswer.md)| The answer to the TOTP enrollment specified by totp_id. |
 **user_id** | **str**| Query based on user id | [optional]

### Return type

[**TOTPEnrollment**](TOTPEnrollment.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The TOTP enrollment was was updated. |  -  |
**400** | Incorrect answer to enrollment challenge |  -  |
**404** | Enrollment not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_webauthn_enrollment**
> WebAuthNEnrollment update_webauthn_enrollment(webauthn_id, web_auth_n_enrollment_answer)

Update the WebAuthN enrollment if the answer provided is correct.

Update the WebAuthN enrollment if the answer provided is correct. This completes the device enrollment.

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import challenges_api
from agilicus_api.model.web_auth_n_enrollment import WebAuthNEnrollment
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.web_auth_n_enrollment_answer import WebAuthNEnrollmentAnswer
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
    api_instance = challenges_api.ChallengesApi(api_client)
    webauthn_id = "AbasaWlLLS" # str | A webauthn id found in a path.
    web_auth_n_enrollment_answer = WebAuthNEnrollmentAnswer(
        credential_id='YQ==',
        client_data="client_data_example",
        authenticator_data="authenticator_data_example",
        signature="signature_example",
        user_handle="user_handle_example",
        transports=[
            "ble",
        ],
    ) # WebAuthNEnrollmentAnswer | The answer to the WebAuthN enrollment specified by webauthn_id.
    user_id = "1234" # str | Query based on user id (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update the WebAuthN enrollment if the answer provided is correct.
        api_response = api_instance.update_webauthn_enrollment(webauthn_id, web_auth_n_enrollment_answer)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->update_webauthn_enrollment: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update the WebAuthN enrollment if the answer provided is correct.
        api_response = api_instance.update_webauthn_enrollment(webauthn_id, web_auth_n_enrollment_answer, user_id=user_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling ChallengesApi->update_webauthn_enrollment: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webauthn_id** | **str**| A webauthn id found in a path. |
 **web_auth_n_enrollment_answer** | [**WebAuthNEnrollmentAnswer**](WebAuthNEnrollmentAnswer.md)| The answer to the WebAuthN enrollment specified by webauthn_id. |
 **user_id** | **str**| Query based on user id | [optional]

### Return type

[**WebAuthNEnrollment**](WebAuthNEnrollment.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The TOTP enrollment was was updated. |  -  |
**400** | Incorrect answer to enrollment challenge |  -  |
**404** | Enrollment not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

