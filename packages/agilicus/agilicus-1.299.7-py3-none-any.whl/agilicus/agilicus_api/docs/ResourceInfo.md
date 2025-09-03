# ResourceInfo

ResourceInfo holds information about the resource granted permission by a RenderedRule. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_id** | **str** | The unique identifier of the resource. | [readonly] 
**resource_org_id** | **str** | The organisation id corresponding to the organisation which administers the resource granted permissions by this.  | [readonly] 
**resource_type** | **str** | The type of resource. This describes how the resource can be accessed, its purpose, etc. In this particular context, it is useful mostly for display purposes.  | [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


