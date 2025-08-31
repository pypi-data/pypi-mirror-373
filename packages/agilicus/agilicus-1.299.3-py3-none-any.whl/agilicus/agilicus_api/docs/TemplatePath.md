# TemplatePath

A template-based path. A templated path uses `{name}` to indicate a portion of the path to extract for further evaluation. E.g. /collection/{guid}/subcollection/{sub_guid} would match any values of guid and sub_guid, and would keep those values for future use in an extractor. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template** | **str** | The path to template on. Indicate a template with {}. | 
**prefix** | **bool** | Whether to match the template as a prefix. I.e. if &#x60;prefix&#x60; is &#x60;true&#x60;, then &#x60;/collection/{guid}/subcollection/{sub_guid}&#x60; would match &#x60;/collection/1/subcollection/2/stuff&#x60;, whereas if &#x60;prefix&#x60; is &#x60;false&#x60;, then it would not match.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


