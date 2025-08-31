# LicenseConstraint

A constraint provided by a license. A license constraint is a CEL expression which can be used to evaluate various boolean questions, or return numeric information. The system renders the constraints prior to returning them for evaluation. This process involves collecting all constraints from various sources, merging them by name, then applying substitution as needed.  When two constraints share a name, the highest priority one is chosen. If two constraints share a name and a priority, then tie is broken in the following order, with the first being the highest priority.  - organisation level  - license level  - billing account level  - product level  - feature level  - table level  For example, if `max_resources` is defined as `'10000'` at the table level, 100 at the product level, and 1000 at the license level for license A, but not at all for license B, then license A would have `max_resources: 1000`, and license B would have `max_resources: 100`. This allows for defining  consistent, global limits which may be overridden on a case-by-case basis. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**LicenseConstraintName**](LicenseConstraintName.md) |  | 
**expression** | [**LicenseConstraintExpression**](LicenseConstraintExpression.md) |  | 
**priority** | **int** | The priority of this constraint compared to other constraints of the same name.  | 
**comment** | **str** | An optional comment providing insight into the expression | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


