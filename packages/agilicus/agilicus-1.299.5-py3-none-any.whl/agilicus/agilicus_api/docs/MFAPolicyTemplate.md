# MFAPolicyTemplate

Requires that users present a second factor within the given time period when trying to access resources matching the provided labels 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**seconds_since_last_challenge** | **int** | Challenge the user if they have not presented a second factor for the current session in the last N seconds.  | 
**labels** | [**[LabelName]**](LabelName.md) | Restrict the challenge to accesses for resources with one of these labels.  | 
**template_type** | **str** | The descriminator for the PolicyTemplate. Set this to &#x60;mfa&#x60; | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


