# DisplayInfo

Provides customisation for how a resource is displayed to the user. For example, use this to control the icons which represent a resource in different contexts. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**icons** | [**[Icon]**](Icon.md) | The list of icons for this resource. Each icon is associated with a purpose describing how it should be used. Typically client software will select the icon described by the purpose. The order of the icons is stable. Typically software can choose to use the first icon that exists and matches its selection criteria.  | 
**hide** | **str** | Whether or not this Resource is visible in profile/desktop. - &#39;no&#39; or &#39;&#39; or not exists, resource is not hidden - &#39;all&#39; resource is hidden in both profile and desktop - &#39;profile&#39; profile resources are hidden, visible in desktop - &#39;desktop&#39; desktop resources are hidden, visible in profile  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


