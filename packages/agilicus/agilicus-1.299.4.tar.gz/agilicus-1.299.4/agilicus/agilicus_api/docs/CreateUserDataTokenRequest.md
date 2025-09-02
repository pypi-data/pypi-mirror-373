# CreateUserDataTokenRequest

Request object to create a User Data Token

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**audiences** | **[str]** | array of audiences | [optional] 
**token_validity** | [**TokenValidity**](TokenValidity.md) |  | [optional] 
**user_data** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | User data added to token that will be signed. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


