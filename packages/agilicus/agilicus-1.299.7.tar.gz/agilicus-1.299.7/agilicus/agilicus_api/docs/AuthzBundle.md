# AuthzBundle

The Policy Config Authz backend data. This contains various objects (maps) that map respective objects and their guids to the data. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | [optional] [readonly] 
**user_data** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] 
**organisations** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] 
**issuer_upstreams** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] 
**standalone_ruleset_bundles** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] 
**resources** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] 
**resource_urls** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] 
**labelled_objects** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


