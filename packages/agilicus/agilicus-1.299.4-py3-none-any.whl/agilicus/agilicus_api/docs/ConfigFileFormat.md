# ConfigFileFormat

The format of the configuration file. Different servers and resources may require different configuration formats. This allows the user to request the approriate type. Note that not all formats are supported for each resource. The API will return a 400 indicating that the format is unsupported in that case when requesting a configuration of that type.  Types:   - win-reg: A windows registry file. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | The format of the configuration file. Different servers and resources may require different configuration formats. This allows the user to request the approriate type. Note that not all formats are supported for each resource. The API will return a 400 indicating that the format is unsupported in that case when requesting a configuration of that type.  Types:   - win-reg: A windows registry file.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


