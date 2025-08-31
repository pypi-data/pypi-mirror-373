# ProductTableVersionSpec

The specification of a ProductTableVersion. This includes the actual ProductTable, alongside information like the version. The version determines which ProductTableVersion is used by default. The system uses the most recent product table according to the version. That is, it sorts by version descending, then uses the top item. Only versions which are published will be used. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**version** | [**ProductTableVersionString**](ProductTableVersionString.md) |  | 
**product_table** | [**ProductTable**](ProductTable.md) |  | 
**published** | **bool** | Whether or not to consider this version for new licenses.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


