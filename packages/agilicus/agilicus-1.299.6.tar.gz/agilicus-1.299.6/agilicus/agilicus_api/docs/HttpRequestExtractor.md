# HttpRequestExtractor

Specifies a piece of information to extract from a request. Gives it a name and a type. The extracted information is then used, by name, in a RuleMatcher. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the extracted value. | 
**value_type** | **str** | The expected type of the value. If the value does not match the given type, then it will not be populated for matching. By default, all values are converted from their javascript representation.  &#x60;any&#x60;: A value of any type &#x60;integer&#x60;: An integer value &#x60;string&#x60;: A string type &#x60;list&#x60;: A list value of any type &#x60;object&#x60;: an object value containing values of any type  | 
**source** | [**HttpRequestExtractorSource**](HttpRequestExtractorSource.md) |  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


