# Audit

An audit record containing information about a single action performed in the system.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The id of the user performing the action | [optional] [readonly] 
**target_resource_type** | **str** | The name of the resource type which was affected by the event which generated this record. The &#x60;target_id&#x60; field will uniquely identify, if possible, the record within the resource type.  | [optional] [readonly] 
**target_resource_org_id** | **str** | The org_id associated with the target_id/target_resource_type.  | [optional] [readonly] 
**target_resource_name** | **str, none_type** | The human friendly name assigned to the resource. | [optional] 
**api_name** | **str** | The name of the API which generated the event. This will typically be a single value for many different target_resource_types.  | [optional] [readonly] 
**org_id** | **str** | The organization of the user performing the action | [optional] [readonly] 
**time** | **datetime** | the time at which the log was generated | [optional] [readonly] 
**action** | **str** | The type of action performed on the target | [optional] 
**source_ip** | **str** | The IP address of the host initating the action | [optional] [readonly] 
**target_id** | **str** | The id of the resource affected by the action | [optional] [readonly] 
**token_id** | **str** | The id of the bearer token used to authenticate when performing the action | [optional] [readonly] 
**trace_id** | **str** | A correlation ID associated with requests related to this action | [optional] [readonly] 
**session** | **str** | The session associated with this action. Sessions typically span multiple tokens.  | [optional] [readonly] 
**secondary_id** | **str** | The secondary id of the resource affected by the action if one exists. This can occur if the resource&#39;s primary key is a composite key. APIs whose resources are not referenced by a GUID in the path make use of these fields for example the replace_user_role endpoint uses the user_id, and application to identify a resource.  | [optional] [readonly] 
**tertiary_id** | **str** | The tertiary id of the resource affected by the action if one exists. This can occur if the resource&#39;s primary key is a composite key.  | [optional] [readonly] 
**parent_id** | **str** | The id of the parent resource for the resource affected by the action. An example of this is the path /v1/collection/2jkdcmwB97jh3kiglnz/subcollection/idabc123. The resource belongs to the &#x60;subcollection&#x60; which falls under the parent in this case &#x60;collection&#x60;. As a resulti idabc123 is the target_id, 2jkdCmwB9u7Jh3KIglNZ is the parent ID  | [optional] [readonly] 
**grandparent_id** | **str** | The id of the grandparent resource for the resource affected by the action. An example of this is the path /v1/collection/2jkdcmwB97jh3kiglnz/subcollection/2334115135/subsubcolletion/aaabbbccc Similar to the parent id example  aaabbbccc is the target_id, 2334115135 is the parent ID and 2jkdcmwB97jh3kiglnz is the grandparent_id  | [optional] [readonly] 
**audit_attributes** | [**[AuditAttribute]**](AuditAttribute.md) | A list of AuditAttributes | [optional] 
**description** | **str** | A human readable summary of this audit. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


