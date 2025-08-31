# TokenReissueRequest

A request to reissue a token. This contains the existing token from which the new token will be created, and any parameters to change the scope of the token. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token** | **str** | The existing opaque token used to create the new one. This should be the same token you would normally use to make API calls.  | 
**org_id** | **str** | The id of the Organisation on which you want to operate with the new token. Make sure you have permissions in this organisation; otherwise the request will fail.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


