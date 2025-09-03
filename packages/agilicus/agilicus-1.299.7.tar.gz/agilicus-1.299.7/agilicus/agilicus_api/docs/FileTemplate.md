# FileTemplate

A FileTemplate defines a templated file which maps a single file stored in the API to a set of rendered files whose structure is defined by the stored file, and whose content is a result of filling in the template's parameters with arguments provided in the request to render it. Templates are text files, with a special syntax describing how to fill in the  parameters.   Archives:   The underyling File in the API may be an archive (such as a zip), in which case each file   will be rendered in turn, unless the template indicates that only a subset of files should be modified,   or the request itself asks for only a file within the archive.  Rendering:   The process of rendering a template involves collecting the template arguments from the   request and static context, merging them, then running the resulting set through a template   engine. The merge process is straightforward. Each argument has a name. The argument set   has exactly one value per name. If two arguments have the same name, the resulting argument   set uses the value with the highest priority. The request data has higher priority than the   static context. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**FileTemplateSpec**](FileTemplateSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


