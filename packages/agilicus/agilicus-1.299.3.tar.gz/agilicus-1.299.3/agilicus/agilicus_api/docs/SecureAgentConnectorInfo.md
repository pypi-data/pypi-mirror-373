# SecureAgentConnectorInfo

Information necessary for the Secure Agent to connector a given connector. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connection_uri** | **str** | The URI used to establish a connection to the connector. | 
**max_number_connections** | **int** | The maximum number of connections to maintain to the cluster when stable. Note that this value may be exceeded during times of reconfiguration. A value of zero means that the connector is effectively unused by this Secure Agent.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


