# OrganisationSystemOptions

Organisation System Options are are properties of the organisation controlled by the system and are not configurable by end user.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier | [optional] [readonly] 
**new_subscription_feature_overrides** | **[str], none_type** | A list of features to apply to new subscriptions that are created from this organisation. | [optional] 
**allowed_domains** | **[str]** | A list of domains whose subdomains are allowed to build fully qualified domain names for resources in this organisation  | [optional] 
**license_constraints** | [**[LicenseConstraint]**](LicenseConstraint.md) | Overrides for constraints applied to this org&#39;s license. Only use in exceptional circumstances.  | [optional] 
**constraint_variables** | [**LicenseConstraintVariables**](LicenseConstraintVariables.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


