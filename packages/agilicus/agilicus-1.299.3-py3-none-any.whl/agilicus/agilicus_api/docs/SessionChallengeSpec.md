# SessionChallengeSpec

Session Challenge Specification

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**webpush** | **bool** | Create a webpush based session challenge request. This would create another challenge request with answer data, which is then messaged to the user via webpush (messages api). This allows creating session challenges on resources such as RDP and shares, where the client is not a browser.  | [optional] 
**description** | **str** | Description to user as to which can provide info such as which resource this session challege is associated with.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


