# Catalogue

A generic collection of catalogue entries. Entries belonging to the same category should be found in the same catelogue.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier | [optional] [readonly] 
**category** | **str** | The category of catalogue that this catalogue belongs to. | [optional] 
**catalogue_entries** | [**[CatalogueEntry]**](CatalogueEntry.md) | The list of catalogue entries for the catalogue | [optional] [readonly] 
**created** | **datetime** | Creation time | [optional] [readonly] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


