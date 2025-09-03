# ApplicationService

Application service's properties

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the service. Services will be selected and assigned using this. This value must be unique within an organisation.  | 
**org_id** | **str** | The organisation which owns this service. | 
**created** | **datetime** | Creation time | [optional] [readonly] 
**id** | **str** | Unique identifier | [optional] [readonly] 
**hostname** | **str** | The hostname of the service. Your applications will refer to this service using its hostname. This can also be the IP Address of the service. If the address is an IPv4 Address it will add the IP to the ipv4_addresses field and set the name_resolution to static  | [optional] 
**ipv4_addresses** | **[str]** | The IPv4 addresses of &#x60;hostname&#x60; within the data center. | [optional] 
**name_resolution** | **str** | How to resolve the hostname of the service. If static, then ipv4_address will be used. Otherwise, if dns the Organisation&#39;s dns services will be queried.  | [optional]  if omitted the server will use the default value of "static"
**config** | [**NetworkServiceConfig**](NetworkServiceConfig.md) |  | [optional] 
**port** | **int** | The transport-layer port on which to access the service. exclusiveMinimum: 0 exclusiveMaximum: 65536  | [optional] 
**protocol** | **str** | The transport-layer protocol over which to communicate with the service.  | [optional]  if omitted the server will use the default value of "tcp"
**assignments** | [**[ApplicationServiceAssignment]**](ApplicationServiceAssignment.md) | The Application Environments which have access to this ApplicationService. Manipulate this list to add or remove access to the ApplicationService.  | [optional] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**service_type** | **str** | The type of application service. This refers to how the application connects to the service | [optional] 
**service_protocol_type** | **str** | The protocol carried by this service. This indicates to the Agilicus infrastructure how to interpret the data being transmitted to the service. Different protocols have different subclasses of an ApplicationService used to configure that protocol&#39;s details. This field may take on the following values:   - ip: Any upper layer protocols are transparent to the Agilicus infrastructure.     Agilicus does not participate in the protocol.   - fileshare: The service is a fileshare. Agilicus will participate in the file sharing     protocol in order to expose the fileshare to the Internet.   - desktop: The service is a desktop. Agilicus provides a Desktop Gateway allowing users to access     their Desktop without them being directly exposed to the internet. Users connect to this service     through the Desktop Gateway, using a protocol such as the Remote Desktop Protocol.  | [optional] [readonly] 
**tls_enabled** | **bool** | Whether Transport Layer Security (TLS) is enabled for this ip service running over tcp. This field has no meaning for non-ip services, or services using a transport protocol other than tcp.  | [optional] 
**tls_verify** | **bool** | Whether the certificate presented by the Service is verified by the infrastructure. This can be useful when interacting with a test server which may not have a production certificate signed by a public certificate authority.  | [optional] 
**connector_id** | **str** | Unique identifier | [optional] 
**connector_instance_id** | **str** | Assign network resource to a specific instance. This instance MUST be within the defined connector_id above. This allows further refinement for assignment, in case a connector is HA, and a service may only traverse one of the instances.  | [optional] 
**protocol_config** | [**ServiceProtocolConfig**](ServiceProtocolConfig.md) |  | [optional] 
**connection_uri** | **str** | The URI by which this service can be directly accessed. Depending on the type of connector associated with this service, the URI could be public or internal to the Agilicus infrastructure. In both cases, valid credentials proving permission to access this service are necessary to access the service. If this field is empty, then it cannot be accessed directly..  | [optional] [readonly] 
**connection_host_aliases** | **[str]** | A list of hosts for which the assigned connector will also forward requests for this application service.  | [optional] [readonly] 
**resource_config** | [**ResourceConfig**](ResourceConfig.md) |  | [optional] 
**alternate_mode_setting** | [**AlternateModeSetting**](AlternateModeSetting.md) |  | [optional] 
**stats** | [**ApplicationServiceStats**](ApplicationServiceStats.md) |  | [optional] 
**status** | [**ApplicationServiceStatus**](ApplicationServiceStatus.md) |  | [optional] 
**connector_service** | **str** | This connector service refers to a connector service name that is bound to a connector_id. For example, &#39;audits&#39;, would refer to the audits service found on a connector for connector to connector audit routing.  | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


