# AuditAttribute

An audit attribute associated with an audit record. An attribute provides additional information associated with the audit that is specific to the type of audit recorded.  For example, when a role is added to a user, a role 'CREATE' event would be created, including attributes for:    - attribute for the application/resource associated with role    - attribute for the user associated with the user receiving the role    - attribute for the role itself, defining what actual role was received 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**attribute_id** | **str** | The id of the associated attribute. | [optional] [readonly] 
**attribute_type** | **str** | The name of the attribute type.  | [optional] [readonly] 
**attribute_org_id** | **str, none_type** | The org_id associated with this audit attribute. | [optional] [readonly] 
**attribute_name** | **str, none_type** | The name of the attribute. | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


