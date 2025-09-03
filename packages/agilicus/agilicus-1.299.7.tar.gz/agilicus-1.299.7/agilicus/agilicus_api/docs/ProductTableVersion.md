# ProductTableVersion

A version of the Product Table. A product table describes the properties of the products offered by Agilicus alongside their respective features and constraints. It is a table in that typically each product has a set of contraints related to each feature.  When customers subscribe to Agilicus, they choose a Product. At this time they are granted a License linked to that product for the latest version of the ProductTable. When new versions of the ProductTable are published, existing licenses are unchanged: they continue to use the version with which they were previously associated.  ProductTableVersions are published and modified atomically. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**ProductTableVersionSpec**](ProductTableVersionSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


