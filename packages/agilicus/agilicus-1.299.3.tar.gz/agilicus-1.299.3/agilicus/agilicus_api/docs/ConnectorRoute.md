# ConnectorRoute

Describes a route by which a resource can be accessed 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**resource_id** | **str** | Unique identifier | 
**routing_path** | **str** | The path uniquely identifying the route to the mentioned resource using the routing given routing_method. This path must be joined with a host and scheme associated to a connector router to actually establish a tunnel.  | 
**routing_method** | **str** | How to determine the route given the routing_path. The possible values mean:   - &#x60;resource_hostname&#x60;: route based on the hostname configured for the resource.      example: /named-service/org-1/host/localhost/port/5000   - &#x60;resource_id&#x60;: route based on the id of the resource.      example: /named-service/org-1/guid/aB8Zm5tuxVia2FQ7i/port/5000 Note that it may indicate a port range, (e.g. /named-service/&lt;org&gt;/host/localhost/port/{{port}}?port:int&#x3D;5000-5002,5555,5556). In that case when establishing an actual connection, substitute {{port}} with the port you want to connect to, and drop the query string.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


