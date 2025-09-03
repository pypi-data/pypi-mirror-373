# SSHResourceStatus

Derived, read-only properties of a SSHResource. Use these to determine how to interact with a DesktopResource, or to see its current state. If you have not assigned the SSHResource to a Connector, then some of its status will not be availble. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gateway_uri** | **str** | The base uri at which to access the gateway for this SSHResource.  | [optional] 
**connection_uri** | **str** | The URI by which this resource can be directly accessed. Depending on the type of connector associated with the resource, the URI could be public or internal to the Agilicus infrastructure. In both cases, valid credentials proving permission to access this service are necessary to access the service. If this field is empty, then it cannot be accessed directly.  | [optional] 
**stats** | [**SSHResourceStats**](SSHResourceStats.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


