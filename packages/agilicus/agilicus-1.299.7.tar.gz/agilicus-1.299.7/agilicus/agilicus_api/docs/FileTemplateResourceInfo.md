# FileTemplateResourceInfo

Context information about a resource for a template argument. Populating this provides access to:   - \"resource.id\"  - \"resource.name\"  - \"resource.org_id\"  - \"resource.uri.domain\"  - \"resource.uri.scheme\"  - \"resource.uri\"  - \"resource.type\"  - \"user_resource_info.X\" where X is an attribute of the UserResourceAccessInfoStatus 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | [optional] 
**resource_id** | **str** | Unique identifier | [optional] 
**name** | **str** |  | [optional] 
**uri** | **str** | The URI for the resource | [optional] 
**resource_type** | **str** | The type of the resource | [optional] 
**user_resource_info** | [**UserResourceAccessInfoStatus**](UserResourceAccessInfoStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


