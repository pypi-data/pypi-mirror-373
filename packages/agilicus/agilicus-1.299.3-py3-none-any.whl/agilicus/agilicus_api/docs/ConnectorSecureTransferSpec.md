# ConnectorSecureTransferSpec

The specification of the ConnectorSecureTransfer

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connector_id** | **str** | Unique identifier | [readonly] 
**org_id** | **str** | Unique identifier | 
**src_instance_id** | **str** | Unique identifier | [optional] 
**src_public_key** | **str** | The source instance public key | [optional] 
**dst_instance_id** | **str** | Unique identifier | [optional] 
**dst_public_key** | **str** | The destination instance public key | [optional] 
**transfer_type** | **str** | The type of data to be transfered. Note that this field only has meaning to the source and destination. Supports:    - &#39;private_key&#39;  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


