# ServiceAccountSpec

The configuration object for a service account. A service account has the same properties of a user.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the service account. This will be used as part of the generated email for the service account. Note the service account&#39;s email will not be updated after it has been created.  | 
**org_id** | **str** | The unique id of the Organisation to which this service account belongs to. This restricts the possible values for allowed_sub_orgs  | 
**enabled** | **bool** | Enable/Disable a service account. This will enable/disable the service account user associated with this account. | [optional] 
**allowed_sub_orgs** | **[str]** | The list of suborgs that this service account can be used in. To enable this service account in a sub organisation, activate this service account&#39;s user in the organisation. | [optional] 
**inheritable_config** | [**InheritableUserConfig**](InheritableUserConfig.md) |  | [optional] 
**protected_by_id** | **str, none_type** | The unique id of the object that is using this service account. This protects the service account from being deleted inadvertently unless the service account is explicitly deleted by utilizing the delete optional arguments that provide the protected_by_id and protected_by_type.  | [optional] 
**protected_by_type** | **str, none_type** | The protected_by_id object type that is using this service account. This protects the service account from being deleted inadvertently unless the service account is explicitly deleted by utilizing the delete optional arguments that provide the proteted_by_id and protected_by_type.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


