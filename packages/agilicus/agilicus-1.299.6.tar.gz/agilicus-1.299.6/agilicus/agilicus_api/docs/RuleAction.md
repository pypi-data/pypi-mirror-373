# RuleAction

An action to take when a rule evaluates to true. The `action` field determine which action is taken. Other fields may influence the behaviour of the action. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**action** | **str** | The name of the action to take. This controls the behaviour. - &#x60;allow&#x60;: allow the request - &#x60;deny&#x60;: deny the request - &#x60;redirect&#x60;: redirect the request. This action causes the rules engine to immediately respond to the request with an HTTP redirect pointing to path. The request is not proxied. - &#x60;log&#x60;: log the request - &#x60;none&#x60;: do nothing. This is useful for parent rules which essentially annotate sub-rules with   shared conditions. - &#x60;revocation_check&#x60;: checks whether the request and response are valid according to revocation protocols   such as CRL or OCSP. - &#x60;mfa&#x60;: require mfa  | 
**log_message** | **str** | The message to log. If multiple actions output a log, the messages will be combined using a \&quot;,\&quot; to separate them.  | [optional] 
**path** | **str** | The path to use in related actions.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


