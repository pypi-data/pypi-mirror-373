# PolicyTemplateInstance

A policy template. Each PolicyTemplateInstance instantiates a specific precanned set of policy constructs which compose the overall policy for an organistion. For example you can create a PolicyTemplateInsance which defines the parameters of a template which defines when a user must present a second factor when accesing a resource.  Mulitple insances of a given template can coexist. They can be updated and deleted independently as requirements change.  A template is uniquely identified by a 'name' passed at instantiation time.`  By default, template instances are hooked into the global policy of the organisation. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**PolicyTemplateInstanceSpec**](PolicyTemplateInstanceSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


