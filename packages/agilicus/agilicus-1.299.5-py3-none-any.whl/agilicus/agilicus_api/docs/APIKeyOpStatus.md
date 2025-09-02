# APIKeyOpStatus

The operational status of an API Key.  - `expired`: The API Key has expired. It may no longer be used. - `revoked`: The API Key has been revoked. It may not longer be used. - `disabled`: The API Key has been disabled. It may not be used until it is re-enabled. - `active`: The API Key is active. It may be used. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | The operational status of an API Key.  - &#x60;expired&#x60;: The API Key has expired. It may no longer be used. - &#x60;revoked&#x60;: The API Key has been revoked. It may not longer be used. - &#x60;disabled&#x60;: The API Key has been disabled. It may not be used until it is re-enabled. - &#x60;active&#x60;: The API Key is active. It may be used.  |  must be one of ["expired", "revoked", "disabled", "active", ]
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


