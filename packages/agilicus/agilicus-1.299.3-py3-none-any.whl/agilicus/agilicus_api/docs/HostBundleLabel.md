# HostBundleLabel

A label that is part of a bundle 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exclude** | **bool** | if true, the hosts with the label are excluded from the bundle. When a label is excluded, it takes precendence over included rules, such that if a hosts were to labeled with both an exclude and not exclude label, the result would be that host to be excluded.  | [optional] 
**label** | [**HostLabelSpec**](HostLabelSpec.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


