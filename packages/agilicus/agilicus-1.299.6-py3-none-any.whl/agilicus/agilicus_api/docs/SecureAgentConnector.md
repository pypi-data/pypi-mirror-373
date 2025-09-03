# SecureAgentConnector

A connector establishes a tunnel between the Agilicus infrastructure and the Secure Agent running on site. Its configuration controls how that link is established, how many connections are maintained and so on. Typically a connector corresponds to an Application running in the Agilicus infrastructure which provides the ingress side of the Secure Agent tunnel. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**max_number_connections** | **int** | The maximum number of connections to maintain to the cluster when stable. Note that this value may be exceeded during times of reconfiguration. A value of zero means that the connector is effectively unused by this Secure Agent.  | 
**connection_uri** | **str** | Overrides the default URI used to connect to this connector. This can be used to point the Secure Agent somewhere other than the default.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


