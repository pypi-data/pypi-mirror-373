# ProductTable

A set of LicensedProducts and related LicensedFeatures. The list of features is independent from the list of products. Each product selects a subset of features. Given a product, a license determines what features it provides and the constraints on them by combining the information (particularly constraints) from the product with the set of features. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**products** | [**[LicensedProduct]**](LicensedProduct.md) | The products provided by the table  | 
**features** | [**[LicensedFeature]**](LicensedFeature.md) | The features provided by the table  | 
**constraint_variables** | [**LicenseConstraintVariables**](LicenseConstraintVariables.md) |  | [optional] 
**global_constraints** | [**[LicenseConstraint]**](LicenseConstraint.md) | Constraints which apply to all products and versions  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


