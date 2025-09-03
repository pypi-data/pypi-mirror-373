# RoutingRequest

On organisation signup, a user will require a regional or pop domain relevant for their ip address location.  This request allows the user to provide their IP addresses, and the response provided will be possible pops or regions that could match. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ip_addresses** | **[str]** | A list of ip addresses associated with the request | 
**point_of_presences** | [**[PointOfPresence]**](PointOfPresence.md) | The list of point of presences that can support the ip addresses | [optional] [readonly] 
**regions** | [**[Region]**](Region.md) | The list of regions that can support the ip addresses | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


