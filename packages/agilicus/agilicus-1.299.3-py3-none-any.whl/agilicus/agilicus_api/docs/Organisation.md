# Organisation

 Object describing the properties of an organisation  point_of_presence_name:  An Organisation can be assigned to a PointOfPresence, with the property point_of_presence_id. region_name:  An Organisation can be assigned to a Region, with the property region_id. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier | [optional] [readonly] 
**all_users_group_id** | **str** | group id of group containing this organisations all users | [optional] 
**all_users_all_suborgs_group_id** | **str** | group id of group containing this organisations all users including all sub organisations | [optional] 
**all_users_direct_suborgs_group_id** | **str** | group id of group containing this organisations all users including only direct sub organisations | [optional] 
**auto_created_users_group_id** | **str** | group id of group containing users automatically created when they logged in | [optional] 
**external_id** | **str** | External unique identifier | [optional] 
**organisation** | **str** | organisation name | [optional] 
**issuer** | **str** | connect id issuer | [optional] 
**issuer_id** | **str** | Unique identifier | [optional] 
**subdomain** | **str** | Organisations subdomain. Note this must be unique accross all organisations | [optional] 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**created** | **datetime** | Creation time | [optional] [readonly] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**contact_id** | **str** | GUID of the organisation admin | [optional] 
**contact_email** | **str** | The email address of the contact. | [optional] [readonly] 
**parent_id** | **str** | parent organisation id | [optional] 
**root_org_id** | **str** | The id of the organisation at the root of this organisation hierarchy. For example, if A is the parent of B, and B is the parent of C, then A would be the root organisation of A, B and C. Note that this field will be ignored if changed.  | [optional] 
**auto_create** | **bool** | Auto-creates a user | [optional]  if omitted the server will use the default value of False
**trust_on_first_use_duration** | **int** | The time window in seconds which represents the period of time for which a new user is eligible for trust on first use enrollment. The duration will be applied from the user&#39;s created date, or if the user&#39;s enrollment period was reset by an administrator.  | [optional]  if omitted the server will use the default value of 86400
**feature_flags** | [**[FeatureFlag]**](FeatureFlag.md) | A list of features to enable or disable. This is mostly for advanced use. No guarantees exist that a given feature will always exist by a given name, or that it will be configurable.  | [optional] 
**admin_state** | [**OrganisationStateSelector**](OrganisationStateSelector.md) |  | [optional] 
**status** | [**OrganisationStatus**](OrganisationStatus.md) |  | [optional] 
**billing_account_id** | **str** | The billing account id | [optional] 
**billing_subscription_id** | **str** | The billing subscription id | [optional] 
**shard** | **str** | The shard to use on the agilicus platform. This provides logical seperation on the agilicus platform. This can be used to prevent access to applications between suborgs in the same organisation.  | [optional] 
**cluster** | **str** | The agilicus cluster/region to host the platform on. This provides information to determine what physical location any services provided should run from. Consult the list of Regions for the possible values to set here. Changing this value will cause resources to move to the new cluster. Changing the setting will cause a few minutes of downtime while resources are moved. You will have to change the cname for your domain in order to attract traffic to the correct location.  | [optional] 
**configured_capabilities** | [**OrganisationCapabilities**](OrganisationCapabilities.md) |  | [optional] 
**owner_config** | [**OrganisationOwnerConfig**](OrganisationOwnerConfig.md) |  | [optional] 
**product_label_override** | **str** | Override the default product label.  | [optional] 
**system_options** | [**OrganisationSystemOptions**](OrganisationSystemOptions.md) |  | [optional] 
**ruleset_bundle_id** | **str** | Global rules bundle id (see StandaloneRulesetBundle) applied globally across the organisation.  | [optional] 
**point_of_presence_id** | **str** | Unique identifier | [optional] 
**point_of_presence_name** | [**FeatureTagName**](FeatureTagName.md) |  | [optional] 
**region_id** | **str** | Unique identifier | [optional] 
**region_name** | **str** | The region name this organisation is associated with | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


