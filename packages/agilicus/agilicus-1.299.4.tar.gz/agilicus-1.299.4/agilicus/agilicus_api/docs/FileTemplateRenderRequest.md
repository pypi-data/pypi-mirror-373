# FileTemplateRenderRequest

A request to render a file template. The request contains the arguments to provide to the template. The result will contain the binary data. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template_arguments** | [**[FileTemplateArgument]**](FileTemplateArgument.md) | A list of arguments to render the template. The renderer combines these with the template&#39;s default arguments, with the template_arguments taking precedence.  | 
**org_id** | **str** | Unique identifier | 
**resource_information** | [**FileTemplateResourceInfo**](FileTemplateResourceInfo.md) |  | [optional] 
**user_information** | [**User**](User.md) |  | [optional] 
**as_attachment** | **bool** | Set this to true if the client is a browser and you want to trigger a download.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


