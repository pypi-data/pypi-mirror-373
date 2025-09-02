# ResourceConfig

This object provides a container for all common configuration related to a Resource. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**roles_config** | [**RolesConfig**](RolesConfig.md) |  | [optional] 
**rules_config** | [**RulesConfig**](RulesConfig.md) |  | [optional] 
**display_info** | [**DisplayInfo**](DisplayInfo.md) |  | [optional] 
**published** | **str** | Whether or not this Resource is published, and if so, how. A Resource that has been published somewhere will have high level details about it visible, such as its name and description. The enum values mean the following:   - no: This Resource is not published. It will only be visibile to users with       permission to access the Resource, or to administrators.   - public: This Resource is published to the public catalogue. Any user who       can request access to the organisation will see high level details about this       Resource.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


