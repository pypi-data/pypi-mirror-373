# ClusterSpec

Spec for a Cluster.  The name and domain specified for a Cluster defines a CNAME that would be used to route to this Cluster. The CNAME would therefore resolve and provide the ip_addresses. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**Domain**](Domain.md) |  | [optional] 
**domain** | [**Domain**](Domain.md) |  | [optional] 
**config** | [**ClusterConfig**](ClusterConfig.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


