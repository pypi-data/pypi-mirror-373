# HTTPBearerAuth

Configuration for HTTP bearer token authentication (rfc6750). Systems using this will encode the provided token into the `Authorization` header of http requests according to the HTTP bearer token authentication scheme. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**token** | **str** | The bearer token to use in requests. Should conform to b64token in rfc6750 section 2.1.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


