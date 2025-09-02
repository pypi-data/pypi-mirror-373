# IpsecConnection

An IPsec connection

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A descriptive name for the ipsec connection. The name must be a unique within a connectors connections.  | 
**inherit_from** | **str** | Allows inheriting from a named spec object. If any configuration in this object is Null or undefined, it will inherit from the named source that is part of the connector. Loops are not permitted, ie. A-&gt;B-&gt;A, and will result in a bad request.  | [optional] 
**gateway_interface** | [**IpsecGatewayInterface**](IpsecGatewayInterface.md) |  | [optional] 
**spec** | [**IpsecConnectionSpec**](IpsecConnectionSpec.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


