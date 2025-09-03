# BillingAccountSpec

Object describing the spec of a Billing Account

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**customer_id** | **str** | a guid describing the billing customer id | [optional] 
**product_id** | **str** | The Product this BillingAccount is associated with. This property is deprecated. The product_id has been moved to the BilingOrgSubscription. | [optional] 
**dev_mode** | **bool** | Billing account is in dev mode, used for connecting to non-live backend billing API.  | [optional] 
**license_constraints** | [**[LicenseConstraint]**](LicenseConstraint.md) | Overrides for constraints applied to all licenses in this billing account. Only use in exceptional circumstances.  | [optional] 
**constraint_variables** | [**LicenseConstraintVariables**](LicenseConstraintVariables.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


