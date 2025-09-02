# GroupMember


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier | [optional] [readonly] 
**org_id** | **str** | The unique id of the Organisation to which this user belongs.  | [optional] 
**first_name** | **str** | User&#39;s first name | [optional] 
**last_name** | **str** | User&#39;s last name | [optional] 
**full_name** | **str** | User&#39;s full name, combination of first and last name | [optional] 
**email** | [**Email**](Email.md) |  | [optional] 
**display_name** | **str** | A suitable, simplified name of the user that can be used to identify a user. For users of type \&quot;user\&quot;, this would be the users email. For other user types (group), the first_name would be used as the display_name. This does introduce the possiblity that multiple users may have identical display names. In this situation, it would be up to the consumer of this to de-duplicate the users (such as also display the users email alongside).  examples:     display_name: user@example.com     display_name: all_users_group  | [optional] [readonly] 
**type** | **str** | Type of user | [optional] [readonly] 
**upstream_user_identities** | [**[UpstreamUserIdentity]**](UpstreamUserIdentity.md) | The upstream identities this user can use to log in to the system. When a user logs in, their identity in this system will be determined by matching against this list. Note that this implies that entries in this list are globally unique.  | [optional] [readonly] 
**inheritable_config** | [**InheritableUserConfig**](InheritableUserConfig.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


