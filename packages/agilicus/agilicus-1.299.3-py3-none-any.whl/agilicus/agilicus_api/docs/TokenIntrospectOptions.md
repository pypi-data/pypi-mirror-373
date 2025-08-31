# TokenIntrospectOptions

Set of options controling how the token is introspected

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**exclude_roles** | **bool** | Parameter controlling whether to determine the roles during introspection | [optional]  if omitted the server will use the default value of False
**support_http_matchers** | **bool** | Whether http matchers are supported. This can impact what response is returned depending on the type of resource for which the introspect applies. For example, some resources may create a matcher to efficient capture a range of values in a template. If http_matchers are disabled, then an inefficient list of exact matches will be returned instead.  | [optional] 
**target_org_info** | [**OrgInfo**](OrgInfo.md) |  | [optional] 
**no_cache** | **bool** | Request that no cache be used to generate the token introspect.  | [optional]  if omitted the server will use the default value of False
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


