# LicensedProduct

A product purchaed by a customer. Licenses point to products. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**LicensedProductName**](LicensedProductName.md) |  | 
**included_features** | [**[LicensedFeatureName]**](LicensedFeatureName.md) | The features included in this product. This ultimately determines which contraints will be provided when evaluating the license.  | 
**license_constraints** | [**[LicenseConstraint]**](LicenseConstraint.md) | The constraints associated with the product. Can be used to fill in missing details for feature-level constraints.  | 
**constraint_variables** | [**LicenseConstraintVariables**](LicenseConstraintVariables.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


