# CatalogueEntry

An entry in the catalogue. The entries in the catalogue should relate to their catalogues type.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the catalogue entry in a user friendly form | 
**id** | **str** | Unique identifier | [optional] [readonly] 
**catalogue_id** | **str** | Unique identifier | [optional] [readonly] 
**catalogue_category** | **str** | The category of catalogue that this entry is apart of | [optional] [readonly] 
**content** | **str** | The content of the catalogue | [optional] 
**tag** | **str** | A qualifier for the catalogue entry. Used for differentiating between entries of the same name | [optional] 
**short_description** | **str** | A short description of the catalogue entry. | [optional] 
**long_description** | **str** | A detailed description of the catalogue entry | [optional] 
**created** | **datetime** | Creation time | [optional] [readonly] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


