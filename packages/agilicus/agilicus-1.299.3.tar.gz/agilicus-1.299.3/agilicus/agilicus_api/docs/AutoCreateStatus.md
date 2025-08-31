# AutoCreateStatus

Whether to automatically create users, and the status to assign to them when doing so. Users logging in from this upstream will be automatically created according to this setting if they do not already exist in the organisation. The status values have the following meanings:   * `active`: The user will be created with the active status. See UserSummary.status     for more details.   * `pending`: The user will be created with the pending status. See UserSummary.status     for more details.   * `disabled`: The user will be created with the disabled status. See UserSummary.status     for more details.   * `default`: Whether the user is automatically created depends on the organisation's policy. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | Whether to automatically create users, and the status to assign to them when doing so. Users logging in from this upstream will be automatically created according to this setting if they do not already exist in the organisation. The status values have the following meanings:   * &#x60;active&#x60;: The user will be created with the active status. See UserSummary.status     for more details.   * &#x60;pending&#x60;: The user will be created with the pending status. See UserSummary.status     for more details.   * &#x60;disabled&#x60;: The user will be created with the disabled status. See UserSummary.status     for more details.   * &#x60;default&#x60;: Whether the user is automatically created depends on the organisation&#39;s policy.  |  must be one of ["active", "pending", "disabled", "default", ]
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


