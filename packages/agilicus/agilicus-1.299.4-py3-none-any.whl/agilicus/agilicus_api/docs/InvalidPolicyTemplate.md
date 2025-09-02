# InvalidPolicyTemplate

InvalidPolicyTemplate is returned when the system is unable to map an otherwise known policy template to its details. This typically happens when the underlying policy componets have been deleted or corrupted. This templates strives to provide as much detail as possible about the original so that it may be recovered e.g. by replacing it with the desired output. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template_type** | **str** | The descriminator for the PolicyTemplate. Set this to &#x60;invalid&#x60; | 
**original_template_type** | **str** | The original type of the template. | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


