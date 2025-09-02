# ApplicationServiceLocation

Describes how to connect to the application service. An application service may be reachable from multiple locations. Whether or not those locations are avaiable depends on location of the client attempting communication with them. The client should probe to determine the best candidate, likely through proximity, or an approximation such as a happy eyeballs strategy. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**hostname** | **str** | The hostname to contact the service on. This will be used for the TLS SNI field. If no IP address is specified, then it will also be used for a DNS lookup.  | 
**port** | **int** | The port to connect to. If empty, will default to port 443. | [optional] 
**ip_address** | **str** | The IP address to connect to. If this is set, then clients can choose to connect directly to it rather than using DNS to discover the address of the location.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


