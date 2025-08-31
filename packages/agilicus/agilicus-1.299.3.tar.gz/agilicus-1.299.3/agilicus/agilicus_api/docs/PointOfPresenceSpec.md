# PointOfPresenceSpec

The PointOfPresenceSpec describes the properties of a point of presence.  A PointOfPresence can specify a cluster_pool, which specifies which clusters would provide service to its routing. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**FeatureTagName**](FeatureTagName.md) |  | 
**tags** | [**[FeatureTagName]**](FeatureTagName.md) | Properties of the point of presence such as different aspects of its geographical location. These can be used to filter point of presences based on desired properties.  | 
**routing** | [**PointOfPresenceRouting**](PointOfPresenceRouting.md) |  | 
**master_cluster_id** | **str** | Designates a particular cluster in the PointOfPresence as a master.  This property is normally not required when there is a single cluster_id specified in cluster_ids.  This guid must also exist inside cluster_ids.  | [optional] 
**cluster_ids** | **[str]** | the configured cluster ids that are associated to this PointOfPresence  | [optional] 
**org_domains** | [**[Domain]**](Domain.md) | Organisation subdomains supported by this PointOfPresence | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


