# NetworkServiceConfig

Configuration related to a network service. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ports** | [**[NetworkPortRange]**](NetworkPortRange.md) | The port(s) and protocol(s) associated with the network service.  | [optional] 
**source_port_override** | [**[NetworkPortRange]**](NetworkPortRange.md) | A NetworkServiceConfig can provide configuration related to which port the traffic is initially received on, before being tunnelled, and finally destined to the final upstream port (ie. the port config in this structure). Without an override, the source_port being listened on would be identical to the destination port (ie. port). The source_port override allows the listening source port to be changed, in case there is a collision. This override can be configured as a port or range (source_port_override), or the system can dynamically allocate a port if dynamic_source_port_override is specified.  | [optional] 
**dynamic_source_port_override** | **bool** | Whether or not we want the system to dynamically allocate the listening source port, in case there is a collision.  | [optional]  if omitted the server will use the default value of False
**source_address_override** | **str** | If set, override the (local) IP the traffic is initially received on, before being tunnelled. Without an override, the source address being listened on would be localhost, or a dynamic IP chosen to avoid collision.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


