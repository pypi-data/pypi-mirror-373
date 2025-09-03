# UserApplicationAccessInfoStatus

The read-only details of a UserApplicationAcessInfo.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | The unique id of the User to which this record applies.  | 
**org_id** | **str** | The unique id of the Organisation to which this record applies.  | 
**org_name** | **str** | The name of Organisation to which this record applies.  | 
**application_name** | **str** | The name of the application.  | 
**application_url** | **str** | The url of the application  | 
**access_level** | **str** | Whether the user has access, has requested access, etc. The possible values have the following meanings:   - requested: the user has requested access to this instance.   - granted: the user has access to this instance.   - none: the user has no relation to this application.  | 
**resource_id** | **str** | The unique id of the Application to which this record applies.  | [optional] 
**parent_org_id** | **str** | The unique id of the parent of the Organisation to which this record applies. Omitted if the Organisation has no parent.  | [optional] 
**parent_org_name** | **str** | The name of the parent of the Organisation to which this record applies. Omitted if the Organisation has no parent.  | [optional] 
**application_description** | **str** | The description of the application  | [optional] 
**application_category** | **str** | A category used to group similar applications together  | [optional] 
**icon_url** | **str** | A url pointing to an icon representing this application.  | [optional]  if omitted the server will use the default value of "https://storage.googleapis.com/agilicus/logo.svg"
**application_default_role_name** | **str, none_type** | The name of the default role of the application. This will be granted to users by default when their access request has been approved.  | [optional] 
**application_default_role_id** | **str, none_type** | The unique id the default role of the application. This will be granted to users by default when their access request has been approved.  | [optional] 
**roles** | **[str]** | The list of roles held by the user for the given application | [optional] 
**display_info** | [**DisplayInfo**](DisplayInfo.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


