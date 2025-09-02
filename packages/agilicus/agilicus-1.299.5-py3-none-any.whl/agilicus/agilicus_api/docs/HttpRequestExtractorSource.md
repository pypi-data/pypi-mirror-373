# HttpRequestExtractorSource

Specifies how to extract information from an http request, such as retrieving a component of a path 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**location** | **str** | The location in the request from which to retrieve the data.  - &#x60;path&#x60;: retrieve data from the request&#39;s path - &#x60;query&#x60;: retrieve data from the request&#39;s query string  | 
**template_extraction** | [**TemplateExtraction**](TemplateExtraction.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


