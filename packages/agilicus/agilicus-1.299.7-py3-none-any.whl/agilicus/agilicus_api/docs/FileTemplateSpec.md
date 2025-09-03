# FileTemplateSpec

Defines a FileTemplate. The template structure is defined by the linked `template_file`, which must be in the same org as the template spec. `template_file` may be empty, in which case the template will not render. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template_parameters** | [**[FileTemplateParameter]**](FileTemplateParameter.md) | The list of parameters this template will accept. Note that by default the &#x60;user.X&#x60; and &#x60;resource.X&#x60; parameters are always accepted.  | 
**template_content_type** | **str** | The content type to return on read. The template engine will automatically determine whether the content needs to be extracted.  | 
**default_arguments** | [**[FileTemplateArgument]**](FileTemplateArgument.md) | A list of arguments to provide by default when rendering the template. These may be overridden by the render request.  | 
**purpose** | **str** | the purpose of the template. helps with deciding whether it should be used for a given operation.  | 
**org_id** | **str** | Unique identifier | 
**descriptive_text** | **str** | Optionally used by a client to describe the template files to users. For example, the client may provide an action button saying: \&quot;Download Project File\&quot;  | 
**rendered_file_name** | **str** | What to call the rendered file when downloading.  | 
**template_file** | **str** | Unique identifier | [optional] 
**associated_objects** | [**[FileTemplateAssociation]**](FileTemplateAssociation.md) | Objects associated with this file template. Useful for finding relevant templates.  | [optional] 
**delimiter** | **str** | The delimiter used to identify placeholders. For example, if the delimiter is $, the possible placeholders for parameter &#x60;foo&#x60; are: &#x60;&#x60;&#x60;   $foo   ${foo} &#x60;&#x60;&#x60;   If the delimiter is %$ then the placeholders for &#x60;foo&#x60; are: &#x60;&#x60;&#x60; %$foo %${foo} &#x60;&#x60;&#x60;  | [optional]  if omitted the server will use the default value of "$"
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


