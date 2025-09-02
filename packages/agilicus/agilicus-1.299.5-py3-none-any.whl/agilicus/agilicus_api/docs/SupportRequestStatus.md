# SupportRequestStatus

The current status of the support group.  The associating_user field contains the user object corresponding to this support user which associates to, controls permissions for and puts an expiry on the actual user who will be providing support. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**supporting_user_id** | **str** | The id of the User corresponding to the email in SupportRequestSpec to which this support user record applies.  | [optional] 
**support_request_group** | [**UserIdentity**](UserIdentity.md) |  | [optional] 
**oper_state** | **str** | The operational state of the support request. The overall status depending on the admin state of the support request spec and overall acknowledgement state  | [optional] 
**requestor_user_id** | **str** | The user ID of the User requesting support | [optional] 
**requestor_email** | **str** | The email of the User requesting support | [optional] 
**organisation** | **str** | The name of the organisation requesting support | [optional] 
**acknowledgements** | [**[SupportRequestAcknowledgement]**](SupportRequestAcknowledgement.md) | A list of acknowledgements on this support request.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


