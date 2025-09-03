# DesktopClientConfiguration

Contains the information used to generate a configuration file for a client wishing to access a DesktopResource, as well that configuration file itself. The system generates the configuration file when the DesktopClientConfiguration is created. Set the `user_id` to provide credentials for the user in the generated configuration. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | The ID of the organisation which owns this DesktopClient.  | 
**user_id** | **str, none_type** | The ID of the user wishing to access this DesktopResource. If this field is not set, no credentials will be provided in the DesktopClientGeneratedConfiguration.  | [optional] 
**custom_config** | [**[CustomDesktopClientConfig]**](CustomDesktopClientConfig.md) | A list of configuration overrides. The items are applied in order, meaning that if two entries map to the same config item, the later one will override the earlier one. This allows for an inheritence mechanism whereby customer configs are placed into the list in ascending order of precision  | [optional] 
**generated_config** | [**DesktopClientGeneratedConfiguration**](DesktopClientGeneratedConfiguration.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


