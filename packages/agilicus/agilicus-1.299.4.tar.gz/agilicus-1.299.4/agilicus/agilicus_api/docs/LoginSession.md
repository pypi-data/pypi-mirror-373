# LoginSession

Information associated with a user's login session.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**session_id** | **str** | The id of the session. | 
**number_of_logins** | **int** | The number of logins that have occured with this session id | 
**number_of_failed_multi_factor_challenges** | **int** | The number of failed multi-factor authentication challenges that have occured with this session id | 
**single_sign_on_time** | **datetime** | The time of the user&#39;s last login with an upstream identity provider if the policy supported single sign on. | 
**user_is_authenticated** | **bool** | An aggregate condition representing the user&#39;s authentication status in the session. This field is the result of user_is_authenticated_by_upstream OR&#39;d with user_is_authenticated_by_cache  | defaults to False
**user_is_authenticated_by_upstream** | **bool** | Indicates whether the user has been directly authenticated by an upstream identity provider | defaults to False
**user_is_authenticated_by_cache** | **bool** | Indicates whether the user has been authenticated via a cached credential | defaults to False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


