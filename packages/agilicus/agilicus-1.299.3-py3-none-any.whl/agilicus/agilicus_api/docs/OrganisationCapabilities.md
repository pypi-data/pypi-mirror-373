# OrganisationCapabilities

Describes what an organisation is allowed to do:   - What features it can use   - Where it can run things 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**features** | [**[FeatureTagName]**](FeatureTagName.md) | A set of features that an organisation can use. Each part of the system places requirements on features in order to be used. For example, a region may have a set of tags associated with it. For an organisation to use that cluster, the region requires that the organisation have at least one of those tags. For a feature such as ipsec VPNs, they simply require that the organisation have the ipsec_vpn feature tag.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


