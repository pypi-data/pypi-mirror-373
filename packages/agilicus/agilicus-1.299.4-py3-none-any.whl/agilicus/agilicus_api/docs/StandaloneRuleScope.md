# StandaloneRuleScope

An object scope that is applied to an object condition.  The scope uses the following form:    \"urn:agilicus:<resource_type>:<resource_id>:role:<role>\"  wildcards are supported. Ie. all resources:  A scope for owner for all resources:    \"urn:agilicus:*:role:owner\"  A scope for any applications, any role   \"urn:agilicus:application:*:role:*\"  A scope for specific application, any role   \"urn:agilicus:application:guid:role:*\"  A specific resource, and specific role   \"urn:agilicus:application:guid:role:viewer\"  The user is known:   \"urn:agilicus:scope:any_known_user\"  The user has at least one role associated with the resource   \"urn:agilicus:scope:any_resource_user\" 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**value** | **str** | An object scope that is applied to an object condition.  The scope uses the following form:    \&quot;urn:agilicus:&lt;resource_type&gt;:&lt;resource_id&gt;:role:&lt;role&gt;\&quot;  wildcards are supported. Ie. all resources:  A scope for owner for all resources:    \&quot;urn:agilicus:*:role:owner\&quot;  A scope for any applications, any role   \&quot;urn:agilicus:application:*:role:*\&quot;  A scope for specific application, any role   \&quot;urn:agilicus:application:guid:role:*\&quot;  A specific resource, and specific role   \&quot;urn:agilicus:application:guid:role:viewer\&quot;  The user is known:   \&quot;urn:agilicus:scope:any_known_user\&quot;  The user has at least one role associated with the resource   \&quot;urn:agilicus:scope:any_resource_user\&quot;  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


