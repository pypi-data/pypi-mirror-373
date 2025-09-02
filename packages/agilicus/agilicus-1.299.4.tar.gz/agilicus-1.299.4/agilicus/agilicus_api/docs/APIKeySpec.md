# APIKeySpec

The definition of an API Key. This controls how it behaves. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | Unique identifier | 
**org_id** | **str** | Unique identifier | 
**expiry** | **datetime** | The API Key expiry time in UTC. If ommitted the key does not expire. | [optional] 
**session** | **str** | Unique identifier | [optional] 
**scopes** | [**[TokenScope]**](TokenScope.md) | The list of scopes requested for APIKey. Ex. urn:agilicus:users. An optional scope is specified with an ? at the end. Optional scopes are used when the permission is requested but not required. Ex. urn:agilicus:users?. A non-optional scope will cause creation of this API Key to fail if the user does not have that permission in this org.  | [optional] 
**name** | **str** | A meaningful name for the api key. Use this to identify its purpose. The name, if set. An empty string is equivalent to it not being set.  | [optional] 
**label** | **str** | Labels the class of APIKeys into which this falls. Use this to organize keys used for similar purposes.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


