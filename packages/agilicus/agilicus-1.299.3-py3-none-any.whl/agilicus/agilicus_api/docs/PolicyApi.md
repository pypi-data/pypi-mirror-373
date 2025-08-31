# agilicus_api.PolicyApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_challenge_decision**](PolicyApi.md#get_challenge_decision) | **POST** /v1/data/authentication/mfa_policy/allow | evaluate a policy challenge decision
[**get_enrollment_decision**](PolicyApi.md#get_enrollment_decision) | **POST** /v1/data/authentication/enrollment/allow | evaluate a policy enrollment decision
[**map_attributes**](PolicyApi.md#map_attributes) | **POST** /v1/data/authentication/attribute_mapping/map_attributes | map attributes of a user


# **get_challenge_decision**
> MFAChallengeAnswer get_challenge_decision(mfa_challenge_question)

evaluate a policy challenge decision

Evaluate a policy challenge decision to determine if the user should be forced to answer a challenge

### Example

```python
import time
import agilicus_api
from agilicus_api.api import policy_api
from agilicus_api.model.mfa_challenge_question import MFAChallengeQuestion
from agilicus_api.model.mfa_challenge_answer import MFAChallengeAnswer
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = policy_api.PolicyApi(api_client)
    mfa_challenge_question = MFAChallengeQuestion(
        input=MFAChallengeQuestionInput(
            login_info=MFAChallengeQuestionLoginInfo(
                user_preference="organisation_policy",
                client_id="app-1",
                client_guid="absjfladasdf23",
                issuer_org_id="absjfladasdf23",
                issuer_guid="absjfladasdf23",
                org_id="absjfladasdf23",
                user_id="jjkkGmwB9oTJWDjIglTU",
                user_object=User(),
                login_session=LoginSession(
                    session_id="abc123iamaguid",
                    number_of_logins=3,
                    number_of_failed_multi_factor_challenges=3,
                    single_sign_on_time=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
                    user_is_authenticated=False,
                    user_is_authenticated_by_upstream=False,
                    user_is_authenticated_by_cache=False,
                ),
                upstream_idp="city-adfs",
                ip_address="127.0.0.1",
                amr_claim_present=False,
                last_mfa_login=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
                user_mfa_preferences=[
                    MFAChallengeMethod(
                        metadata=MetadataWithId(),
                        spec=MFAChallengeMethodSpec(
                            priority=1,
                            challenge_type="challenge_type_example",
                            endpoint="endpoint_example",
                            origin="agilicus.cloud",
                            nickname="nickname_example",
                            enabled=True,
                        ),
                    ),
                ],
                authenticated_federation_info=AuthenticationFederationInfo(
                    type="support-request",
                    acknowledgements=[
                        SupportRequestAcknowledgement(
                            metadata=MetadataWithId(),
                            spec=SupportRequestAcknowledgementSpec(
                                supporting_user_id="supporting_user_id_example",
                                org_id="org_id_example",
                                support_request_id="support_request_id_example",
                            ),
                            status=SupportRequestAcknowledgementStatus(
                                supporting_user_email=Email("foo@example.com"),
                                expiry=dateutil_parser('2025-01-20T10:00:00-08:00'),
                            ),
                        ),
                    ],
                ),
            ),
        ),
    ) # MFAChallengeQuestion | The MFA Challenge Question to ask

    # example passing only required values which don't have defaults set
    try:
        # evaluate a policy challenge decision
        api_response = api_instance.get_challenge_decision(mfa_challenge_question)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyApi->get_challenge_decision: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mfa_challenge_question** | [**MFAChallengeQuestion**](MFAChallengeQuestion.md)| The MFA Challenge Question to ask |

### Return type

[**MFAChallengeAnswer**](MFAChallengeAnswer.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The challenge policy evaluation was successful |  -  |
**400** | Bad request. See https://www.openpolicyagent.org/docs/latest/rest-api/#get-a-document for details |  -  |
**500** | Server Error. See https://www.openpolicyagent.org/docs/latest/rest-api/#get-a-document for details |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_enrollment_decision**
> MFAEnrollmentAnswer get_enrollment_decision(mfa_enrollment_question)

evaluate a policy enrollment decision

Evaluate a policy enrollment decision to determine if the user should be forced to enroll

### Example

```python
import time
import agilicus_api
from agilicus_api.api import policy_api
from agilicus_api.model.mfa_enrollment_question import MFAEnrollmentQuestion
from agilicus_api.model.mfa_enrollment_answer import MFAEnrollmentAnswer
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = policy_api.PolicyApi(api_client)
    mfa_enrollment_question = MFAEnrollmentQuestion(
        input=MFAEnrollmentQuestionInput(
            login_info=MFAEnrollmentQuestionLoginInfo(
                issuer_org_id="absjfladasdf23",
                enrollment_expiry=dateutil_parser('2015-07-07T15:49:51.23+02:00'),
                user_mfa_methods=["totp","webauthn"],
            ),
        ),
    ) # MFAEnrollmentQuestion | The MFA Enrollment Question to ask

    # example passing only required values which don't have defaults set
    try:
        # evaluate a policy enrollment decision
        api_response = api_instance.get_enrollment_decision(mfa_enrollment_question)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyApi->get_enrollment_decision: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mfa_enrollment_question** | [**MFAEnrollmentQuestion**](MFAEnrollmentQuestion.md)| The MFA Enrollment Question to ask |

### Return type

[**MFAEnrollmentAnswer**](MFAEnrollmentAnswer.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The enrollment policy evaluation was successful |  -  |
**400** | Bad request. See https://www.openpolicyagent.org/docs/latest/rest-api/#get-a-document for details |  -  |
**500** | Server Error. See https://www.openpolicyagent.org/docs/latest/rest-api/#get-a-document for details |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **map_attributes**
> MapAttributesAnswer map_attributes(map_attributes_question)

map attributes of a user

map attributes of a user

### Example

```python
import time
import agilicus_api
from agilicus_api.api import policy_api
from agilicus_api.model.map_attributes_answer import MapAttributesAnswer
from agilicus_api.model.map_attributes_question import MapAttributesQuestion
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = policy_api.PolicyApi(api_client)
    map_attributes_question = MapAttributesQuestion(
        input=MapAttributesQuestionInput(
            login_info=MapAttributesQuestionLoginInfo(
                user_object=UserSummary(),
                client_guid="absjfladasdf23",
                issuer_guid="absjfladasdf23",
            ),
        ),
    ) # MapAttributesQuestion | The attributes to map and information used to gather them

    # example passing only required values which don't have defaults set
    try:
        # map attributes of a user
        api_response = api_instance.map_attributes(map_attributes_question)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling PolicyApi->map_attributes: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **map_attributes_question** | [**MapAttributesQuestion**](MapAttributesQuestion.md)| The attributes to map and information used to gather them |

### Return type

[**MapAttributesAnswer**](MapAttributesAnswer.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The attributes were mapped successfully |  -  |
**400** | Bad request. See https://www.openpolicyagent.org/docs/latest/rest-api/#get-a-document for details |  -  |
**500** | Server Error. See https://www.openpolicyagent.org/docs/latest/rest-api/#get-a-document for details |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

