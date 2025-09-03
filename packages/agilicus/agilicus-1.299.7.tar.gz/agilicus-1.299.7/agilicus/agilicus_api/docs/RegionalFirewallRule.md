# RegionalFirewallRule


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | the name of the rule | [optional] 
**action** | **str** | The action of the rule, supported actions:   - &#39;allow&#39;  | [optional] 
**domains** | [**[Domain]**](Domain.md) | domain(s) associated with the rule. For example, a firewall rule with action &#39;allow&#39; would be required to allow the domain | [optional] 
**subnets** | **[str]** | subnets associated with the rule. | [optional] 
**ports** | **[int]** | ports associated with the rule. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


