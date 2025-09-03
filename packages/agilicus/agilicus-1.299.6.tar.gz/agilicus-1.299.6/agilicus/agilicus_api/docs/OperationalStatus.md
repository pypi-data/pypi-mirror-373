# OperationalStatus

The Operational Status for an Entity. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | The status can have the following values: - A &#x60;good&#x60; status means that no action is neccessary - A &#x60;down&#x60; status indicates that either the AdminStatus for the entity   has is set to &#x60;down&#x60;, or there is a entity accessibility problem   that should be dealt with as soon as possible. - A &#x60;degraded&#x60; status indicates that the entity is operational but running   in non-redundant mode. Note that this alarm would only be valid for   a entity that supports redundancy. - A &#x60;testing&#x60; status indicates the entity the entities AdminStatus has been   placed into &#x60;testing&#x60;. - A &#x60;deleted&#x60; status indicates the entity has been deleted.  | 
**status_change_time** | **datetime, none_type** | The data and time when the status changed in value. | [optional] 
**generation** | **int** | The generation count is incremented periodically by the system as it monitors and verifies the current status.  | [optional] 
**generation_update_time** | **datetime, none_type** | The data and time when the generation count was last updated. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


