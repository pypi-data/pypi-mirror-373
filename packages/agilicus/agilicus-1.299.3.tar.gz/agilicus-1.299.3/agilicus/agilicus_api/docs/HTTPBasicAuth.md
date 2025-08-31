# HTTPBasicAuth

Configuration for HTTP basic authentication (RFC7235). Systems using this will encode the provided username and password into the `Authorization` header of http requests according to the HTTP basic authentication scheme. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**username** | **str** | The user as which to authenticate | 
**password** | **str** | The password with which to authenticate | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


