# OrgInfo

When making a request against a child org as a root org user, a multi-org query is used. This has a scope of \"urn:agilicus:token_payload:multiorg:true\". This paramater indicates what orgs are to be filled out in the token introspection. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**target_orgs** | **[str]** | An exact list of orgs to use for this multi-org query  | [optional] 
**target_domain** | **str** | If target_orgs above cannot be populated (likely no org hint is found in the originating request), this provides a hint as to which domain is asking for the intropsected token.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


