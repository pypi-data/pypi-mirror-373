# ServiceForwarderSpec

The configurable properties of a ServiceForwarder. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the service forwarder. This value must be unique within an organisation.  | 
**org_id** | **str** | The organisation which owns this service forwarder. | 
**bind_address** | **str** | The local bind address that local applications will forward to in order to access the service forwarder.  bind_address default is localhost.  | [optional] 
**port** | **int** | The transport-layer port on which to access the service forwarder. exclusiveMinimum: 0 exclusiveMaximum: 65536 If port is not provided on create, the port will be automatically populated as the port currently configured in the application service. Should the application service have multiple ports, the port to be configured is ambiguous and a 400 will be raised, requiring the user to specific the port in which to forward. If an application_service is not provided, a 400 is raised as the fowarder cannot be created.  | [optional] 
**config** | [**NetworkServiceConfig**](NetworkServiceConfig.md) |  | [optional] 
**protocol** | **str** | The transport-layer protocol being fowarded to the remote application service.  | [optional]  if omitted the server will use the default value of "tcp"
**application_service_id** | **str, none_type** | The application service id that this service forwarder connects to.  | [optional] 
**connector_id** | **str, none_type** | A unique identifier which can be empty. The meaning of it being empty depends on the context in which it is used, but usually it implies that something is not set.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


