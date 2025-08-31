# UpstreamGroupMappingEntry

The mapping between an upsteam group and a group in the Agilicus System

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**priority** | **int** | The priority of the mapping entry. A lower number indicates a higher priority. | 
**upstream_group_name** | **str** | The name of the group in your upstream identity provider that you want to map. This can be in the form of a regular expression capture group. The example value will capture all groups starting with &#39;Company Team&#39; and will use the value in the agilicus_group_name. For example Company Team HR Group will be mapped to Agilicus HR Group when the agilicus_group_name is specified with a matching capture group  | 
**agilicus_group_name** | **str** | The name of the group in the Agilicus system that you want to map to. If the upstream_group_name is a capture group this field can contain those captured values. The match groups are specified by a { followed by the match number followed by a closing } ie {0}  | 
**upstream_name_is_a_guid** | **bool** | Indicates that the supplied upstream_group_name will be found in the list of group IDs | [optional] 
**group_org_id** | **str** | The org id that this group mapping applies to. Only mappings whose org id matches the org id that the user logged into will be mapped. If no scope is specified the org id of the issuer is assumed. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


