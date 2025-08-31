# PublicFileOrgLink

An link configuring one organisation to use another as a source of truth for public file lookups. File lookups against `link_org_id` and the tag specified in `file_tag` will use the matching file for `target_org_d`. Note that if `target_org_id` also has a link, it will be recursively searched. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**PublicFileOrgLinkSpec**](PublicFileOrgLinkSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


