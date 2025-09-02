# TOTPEnrollmentStatus

The status of the Time-based One-time Password enrollment

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**state** | **str** | The state of the TOTP enrollment. - pending: The user has been issued a key to register with their authentication application but have not provided a valid answer. - success: The user has provided a valid answer to the enrollment challenge.  | [optional] 
**key** | **str** | An opaque string used to sync up the user&#39;s application and agilicus&#39;s Time-based One-time Password server. This will only be available when initially creating the resource. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


