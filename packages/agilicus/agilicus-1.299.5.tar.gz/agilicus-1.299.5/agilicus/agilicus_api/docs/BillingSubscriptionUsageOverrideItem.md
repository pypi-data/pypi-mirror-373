# BillingSubscriptionUsageOverrideItem

Override to billing-usage job, including minimum-commit. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metric** | **str** | The stripe metric (e.g. active_users) to override | [optional] 
**min_quantity** | **int** | Usage reported is max(min_quantity, actual_quantity) This provides a committed-usage.  | [optional] 
**max_quantity** | **int** | Usage reported is min(max_quantity, actual_quantity). This provides a cap, not-to-exceed.  | [optional] 
**step_size** | **int, none_type** | If set, the usage is stepped by this amount (e.g. rounded up to a multiple of this bounder).  | [optional] 
**group_by_org** | **bool, none_type** | If set to True, the rules above are applied to each org individually in the subscription. E.g. if there is a parent org with 3 users, and 2 child orgs, each with 1 user... if the &#39;min_quantity&#39; is &#39;5&#39;, if this is False, the summation reported will be 5. If this field is True, the summation reported will be 15. If False or Null, all orgs are amalgamated and then the rules are run. The default is False.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


