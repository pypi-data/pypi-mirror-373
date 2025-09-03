# LicenseSpec

The definition of a License. References a product within a specific product table by name. May override the default constraints if needed. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_table_version** | [**ProductTableVersionString**](ProductTableVersionString.md) |  | 
**product_name** | [**LicensedProductName**](LicensedProductName.md) |  | 
**license_constraints** | [**[LicenseConstraint]**](LicenseConstraint.md) | Overrides for constraints applied to this license. Only use in exceptional circumstances.  | [optional] 
**constraint_variables** | [**LicenseConstraintVariables**](LicenseConstraintVariables.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


