# FileVisibility

Controls how a file is exposed to users. This field can be configured with the following values:    - `public`: The file is available to any users, whether or not they     are authenticated. It is accessible via a public URI.   - `private`: The file is only available to users who have been granted     permission to access it explicitly, or through a role their organisation     has assigned to them. It can only be accessed by downloading it through     the API. Changing this field after the file has been uploaded has no effect. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | Controls how a file is exposed to users. This field can be configured with the following values:    - &#x60;public&#x60;: The file is available to any users, whether or not they     are authenticated. It is accessible via a public URI.   - &#x60;private&#x60;: The file is only available to users who have been granted     permission to access it explicitly, or through a role their organisation     has assigned to them. It can only be accessed by downloading it through     the API. Changing this field after the file has been uploaded has no effect.  | defaults to "private",  must be one of ["public", "private", ]
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


