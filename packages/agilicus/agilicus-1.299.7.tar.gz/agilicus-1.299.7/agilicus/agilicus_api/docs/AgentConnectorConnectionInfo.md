# AgentConnectorConnectionInfo

Connection information pertaining to a Connector

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connection_uri** | **str** | The URI used to establish a connection to the connector. | [optional] 
**connection_location** | **str** | The location (e.g. fully qualified domain name) of the connection. While this matches the location in the &#x60;connection_uri&#x60;, it is provided separately for convenience.  | [optional] 
**connection_path** | **str** | The path of the connection. While this matches the path in the &#x60;connection_uri&#x60;, it is provided separately for convenience.  | [optional] 
**connection_org_id** | **str** | The identifier for the organisation hosting the server side of this connection.  | [optional] 
**connection_app_name** | **str** | The name of the Application (if any) hosting the server side of this connection. Note that not all servers will be hosted by an Application, in which case this will be empty.  | [optional] 
**is_an_auth_service** | **bool** | Indicates that the connection is exposing an authentication service  | [optional]  if omitted the server will use the default value of False
**end_to_end_tls** | **bool** | Controls if the connection is end to end TLS.  | [optional] 
**max_number_connections** | **int** | The maximum number of connections to maintain to the cluster when stable. Note that this value may be exceeded during times of reconfiguration. A value of zero means that the connection is effectively unused by this Secure Agent.  | [optional]  if omitted the server will use the default value of 16
**max_number_dynamic_route_connections** | **int** | The maximum number of connections to maintain to the cluster on a per-router basis when using dynamic routes. Note that this value may be exceeded during times of reconfiguration. A value of zero means that the connection is effectively unused by this Secure Agent.  | [optional]  if omitted the server will use the default value of 2
**ip_services** | [**[ApplicationService]**](ApplicationService.md) | The list of ip services associated with this connection | [optional] 
**file_share_services** | [**[FileShareService]**](FileShareService.md) | The list of fileshare services associated with this connection | [optional] 
**desktop_services** | [**[DesktopResource]**](DesktopResource.md) | The list of (vnc) Desktop services | [optional] 
**ssh_services** | [**[SSHResource]**](SSHResource.md) | The list of ssh services associated with this connection | [optional] 
**database_services** | [**[DatabaseResource]**](DatabaseResource.md) | The list of databases associated with this connection | [optional] 
**application_config** | [**ApplicationConfig**](ApplicationConfig.md) |  | [optional] 
**application_scopes** | **[str]** | A list of scopes to be requested on behalf of the user of the application and as well as configured based on the application launchers that launch this application/environment. This field is only populated on a GET request when the query parameter get_scopes&#x3D;True is passed.  | [optional] [readonly] 
**connection_app_id** | **str** | Unique identifier | [optional] 
**connection_env_name** | **str** | The name of the Environment utilized for this application instance.  | [optional] 
**dynamic_routes** | **bool** | Whether or not dynamic routes are enabled for this tunnel. Dynamic routes control whether routes can be added and removed from a tunnel without restarting it.  | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


