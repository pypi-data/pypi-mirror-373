# SourceISOCountryCodeCondition

Compares against the ISO 3166-1 alpha-2 country code of the country in which the source of a request originated. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition_type** | **str** | The discriminator for the condition | 
**operator** | **str** | How to evaluate the variable against the value. - &#x60;in&#x60;: set membership. Checks that variable is in value, assuming value is a list. - &#x60;not_in&#x60;: set anti-membership. Checks that variable is in value, assuming value is a list.  | 
**value** | **[str]** | The set of country codes to check against | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


