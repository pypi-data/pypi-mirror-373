# HypotheticalLicenseDetailsQuery

Defines a query which allows for returning the LicenseDetails under a hypothetical product table.  The results can be controlled in a few ways:  - constrain_to_version: can be used to test what would happen if all orgs using the provided    version were swapped to the provided hypothetical version.  This enables a few use-cases:    1. When modifying an existing table, only show the results for customers who would actually be affected by applying it.    2. See what would happen when migrating customers with other versions of the table to this version.    3. As a special case of number 2, see what would happen when making an entirely new version then migrating a set of customers to it. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_table_version** | [**ProductTableVersion**](ProductTableVersion.md) |  | 
**license_ids** | **[str]** | List of licenses for which to get details | 
**constrain_to_version** | [**ProductTableVersionString**](ProductTableVersionString.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


