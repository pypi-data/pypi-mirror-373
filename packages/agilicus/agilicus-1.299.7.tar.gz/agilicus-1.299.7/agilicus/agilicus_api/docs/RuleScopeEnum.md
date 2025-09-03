# RuleScopeEnum

When this rule applies. * Rules scoped to `anyone` apply regardless of whether the user is authenticated. * Rules scoped to `assigned_to_user` apply only to users who have been assigned the rule,   e.g. via  role. * Rules scoped to `any_known_user` apply to any user who has authenticated with the   system. * Rules scoped to `any_app_user` apply to any user who has a role in the owning   application. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | When this rule applies. * Rules scoped to &#x60;anyone&#x60; apply regardless of whether the user is authenticated. * Rules scoped to &#x60;assigned_to_user&#x60; apply only to users who have been assigned the rule,   e.g. via  role. * Rules scoped to &#x60;any_known_user&#x60; apply to any user who has authenticated with the   system. * Rules scoped to &#x60;any_app_user&#x60; apply to any user who has a role in the owning   application.  |  must be one of ["anyone", "any_known_user", "any_app_user", "assigned_to_user", ]
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


