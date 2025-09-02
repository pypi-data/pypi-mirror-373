# ReconcileOrgDefaultPolicyRequest

The system associates Organistions with various components of the policy framework on creation. These can fall out of sync for various reasons. This object controls a reconcile process that allows for ensuring that an Organisation is up to date with the defaults after the fact. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | [optional] 
**limit** | **int** | Limit on how many orgs will be considered at a time | [optional]  if omitted the server will use the default value of 100
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


