# PolicyCondition

A condition to be evaluated by the policy engine

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition_type** | **str** | The type of this condition. The type determines how the value will be evaluated. This parameter is case sensitive. | 
**value** | **str** | A JSON string representing the value to compare against. The structure of the comparision and type of the value depends on the condition type. A comparision is done to determine the result of the condition (either &#x60;true&#x60; or &#x60;false&#x60;) | 
**operator** | **str** | The operator used to evaluate this condition. The operator field only applies when the condition type is type_object_attribute. The other types have implied operators. | 
**inverted** | **bool** | This field is deprecated. Whether to invert the condition (ie the not operator). If the condition is &#x60;a &#x3D;&#x3D; b&#x60; inverting the condition results in &#x60;not (a &#x3D;&#x3D; b)&#x60; | [optional]  if omitted the server will use the default value of False
**input_is_list** | **bool** | Whether the input to the condition is in a list. The semantics of the condition when this flag is set is to compare every item in the list to the &#x60;value&#x60; using the &#x60;operator&#x60;. The condition is satisfied if any item in the list evaluates to true  | [optional]  if omitted the server will use the default value of False
**field** | **str** | The object path to a field to use as input to the policy condition. This field only applies when the condition type is type_object_attribute. The supported objects are currently &#x60;users&#x60;, and &#x60;clients&#x60;.  | [optional] 
**created** | **datetime** | Creation time | [optional] [readonly] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


