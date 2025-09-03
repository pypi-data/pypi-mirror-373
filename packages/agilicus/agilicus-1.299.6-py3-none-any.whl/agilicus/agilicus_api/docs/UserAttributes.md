# UserAttributes

UserAttributes hold a list of generic attributes associated with a user. These typically come from an identity provider, but may be provisioned by an admin. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attributes** | [**[UserAttribute]**](UserAttribute.md) | The attributes of the user. Each attribute need not be unique. They will be merged using a json-merge style algorithm.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


