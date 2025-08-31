# FeatureSpec

The specification for a product feature

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The features name | 
**key** | **str** | A feature key | 
**description** | **str** | The description for this feature. | [optional] 
**priority** | **int** | The priority of this feature relative to other features with the same key name. Features with identical key names are evaluated in order of higher priority number to lower priority number.  | [optional]  if omitted the server will use the default value of 0
**value** | [**FeatureValue**](FeatureValue.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


