# ResourceSpec

The configurable properties of a Resource. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The human readable name of the resource. Names are unique for a given resource type within an organisation.  | 
**resource_type** | [**ResourceTypeEnum**](ResourceTypeEnum.md) |  | 
**org_id** | **str** | The unique ID of the organisation which owns this Resource. | 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**not_assignable_perm** | **bool** | Most resources can be assigned permission. However when a resource cannot be assigned a permission, this field is used (set to true), which notifies consumers of this API that the resource cannot be assigned a permission. This field defaults to false.  | [optional] 
**config** | [**ResourceConfig**](ResourceConfig.md) |  | [optional] 
**resource_members** | [**[ResourceMember]**](ResourceMember.md) | A list of resources that are contained or associated with this Resource. | [optional] 
**bundle_id** | **str** | Rules bundle id (see StandaloneRulesetBundle) applied to this resource.  | [optional] 
**demo** | **bool** | When true, the resource is considered a demo resource, and will be auto-deleted after 24 hours.  | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


