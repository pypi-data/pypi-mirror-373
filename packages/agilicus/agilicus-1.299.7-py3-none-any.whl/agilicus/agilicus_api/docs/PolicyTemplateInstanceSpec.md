# PolicyTemplateInstanceSpec

The definition of a PolicyTemplateInstance. `template` defines the concrete parameters of the template as well as its type. The org id defines the organisation to which the template applies.  priority defines how this instance is evaluated relative to others. In particular, a PolicyTemplateInstance with a priority of 1 will be evalated before one with a priority of 0. If unset, the priority defaults to 0.  If object_id is set, the policy will be associated with resources of that ID. If object_type is set, the policy will be associated with resources of that type. Note that this means you can define a policy for all resources of a given type (e.g. ssh) by setting the object_type to \"ssh\" and leaving object_id undefined. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | 
**template** | [**PolicyTemplate**](PolicyTemplate.md) |  | 
**name** | **str** | A short name used to unqiuely identify this instance. May be descriptive, but primarily used for idempotency. Cannot be changed after creation.  | 
**description** | **str** | A brief description of the template | [optional] 
**priority** | **int** | The priority of a rule. Lower numbers are lower priority. The engine evaluates rules in order of highest priority to lowest.  | [optional] 
**object_id** | **str** | Unique identifier | [optional] 
**object_type** | [**EmptiableObjectType**](EmptiableObjectType.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


