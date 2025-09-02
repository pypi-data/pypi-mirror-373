# ApplicationServiceRoutingInfo

Describes how to route to an application service. An application service may be reachable through public endpoints or local ones. This object describes those endpoints. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**locations** | [**[ApplicationServiceLocation]**](ApplicationServiceLocation.md) | The locations by which an end-user may reach the application service.  | 
**exposed_as_hostname** | **str** | The exposed network service hostname. See ServiceExposeConfig.  | [optional] 
**hostname_path** | **str** | The path at which to access this application service by hostname. Note that it may indicate a port range, (e.g. /named-service/&lt;org&gt;/host/localhost/port/{{port}}?port:int&#x3D;5000-5002,5555,5556). In that case when establishing an actual connection, substitute {{port}} with the port you want to connect to, and drop the query string.  | [optional] 
**routes** | [**[ConnectorRoute]**](ConnectorRoute.md) | The routes by which to reach this ApplicationService. These routes can be joined with the locations to build the full tunnel URI.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


