# LicenseDetails

The details of a license from the vantage point of a given organisation.  This takes into account all overrides at every level of the licensing hiearchy (organisation, license, billing account, etc) 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**org_id** | **str** | Unique identifier | [optional] [readonly] 
**license** | [**License**](License.md) |  | [optional] 
**license_constraints** | [**[LicenseConstraint]**](LicenseConstraint.md) | The actual constraints  | [optional] 
**constraint_variables** | [**LicenseConstraintVariables**](LicenseConstraintVariables.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


