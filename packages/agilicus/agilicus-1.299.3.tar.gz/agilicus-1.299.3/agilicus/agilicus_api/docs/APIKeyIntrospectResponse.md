# APIKeyIntrospectResponse

Response object for an API Key instrospection.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sub_org_results** | [**[Token]**](Token.md) | List of sub org&#39;s tokens. Empty if the introspection did not allow for multiple orgs.  | 
**primary_token** | [**Token**](Token.md) |  | 
**raw_token** | **str** | The raw token backing this API Key. This will be passed onwards to upstream endpoints.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


