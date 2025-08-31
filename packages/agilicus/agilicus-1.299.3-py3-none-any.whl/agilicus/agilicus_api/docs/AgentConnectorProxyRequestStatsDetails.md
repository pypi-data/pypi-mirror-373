# AgentConnectorProxyRequestStatsDetails

Detailed statistics for requests handled by an AgentConnector's builtin proxy. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**started** | **int** | The total number of requests started by the proxy | 
**finished** | **int** | The total number of requests finished by the proxy. | 
**status_1xx** | **int** | The number of requests which completed with a status code between 100 and 199  | 
**status_2xx** | **int** | The number of requests which completed with a status code between 200 and 299  | 
**status_3xx** | **int** | The number of requests which completed with a status code between 300 and 399  | 
**status_4xx** | **int** | The number of requests which completed with a status code between 400 and 499  | 
**status_5xx** | **int** | The number of requests which completed with a status code between 500 and 599  | 
**status_unknown** | **int** | The number of requests which completed with an unknown status code  | 
**failed_authentication** | **int** | The number of requests which failed authentication.  | 
**failed_authorisation** | **int** | The number of requests which failed authorisation.  | 
**authz_redirected** | **int** | The number of requests which are redirected during authorisation.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


