# BulkUserMetadata

The parameters for bulk setting metadata for a specific organisation and application. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str, none_type** | The unique id of the Organisation to which this record applies.  | 
**data_type** | **str** | The type of data present in the configuration. This informs consumers of how to use the data present. The &#39;json&#39; type means no internal interpretation is done, it is a string-in/string-out. On query this can be deep-merged with member groups.  | 
**data** | **str** | The string representation of the data. This value is interpretted differently based on the data_type | 
**app_id** | **str, none_type** | The unique id of the application to which this record applies.  | [optional] 
**name** | **str** | A descriptive name for this metadata entry | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


