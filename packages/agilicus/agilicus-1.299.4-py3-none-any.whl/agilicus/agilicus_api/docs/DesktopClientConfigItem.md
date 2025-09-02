# DesktopClientConfigItem

A single config item for a desktop config file. How this is serialized depends on the desktop type. For example, it will be serliazed to: {key}:{config_type}:{value} for RDP, for example. Note that, depending on the type of the desktop, some keys are reserved. Trying to set or clear a reserved key is prohibited. For RDP, the reserved keys are:   - `full address`   - `gatewayhostname`   - `gatewaycredentialsource`   - `gatewayusagemethod`   - `gatewayprofileusagemethod`   - `conncetion type`   - `gatewayaccesstoken`   - `remoteapplicationprogram`   - `remoteapplicationprogram`   - `remoteapplicationcmdline`   - `remoteapplicationmode`   - `remoteapplicationexpandcmdline`   - `remoteapplicationexpandworkingdir`   - `remoteapplicationfile`   - `remoteapplicationname` 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**key** | **str** | The key of the config in the rdp file. | 
**config_type** | **str** | The type of the config in the rdp file. Tells the system how to interpret the value. | 
**value** | **str** | The value of the config item. Note that it may be empty. | 
**operation** | **str** | Whether to set of clear the item. If the item is cleared, it will be removed from the config file entirely, meaning that the system defaults will take effect. Note that in this case &#x60;value&#x60; and &#x60;config_type&#x60; are irrelevant.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


