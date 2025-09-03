# CSPSettings

The definition of an Application's Content Security Policy (CSP). Configure CSP by adding directives, each of which control one piece of the policy. The system combines the directions into the single CSP header: `Content-Security-Policy` 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Whether or not to apply CSP. If disabled, the system will not set the Content-Security-Policy header; any CSP headers added by the application will be passed through unchanged.  | 
**mode** | **str** | Mode configures how the content security policy is enforced, if at all. Its possible values mean the following:   - enforce: Actively enforce the policy. Requests which fail the policy will be blocked.     If a report uri is configured for the policy, reports will be sent to it.   - reportonly: Any requests failing the policy generate reports. They are not blocked.   - disabled: the policy is disabled. Requests which would normally fail are neither blocked     nor reported on.  | 
**directives** | [**[CSPDirective]**](CSPDirective.md) | The directives which make up the policy. The system merges each directive into a single header by separating them with the &#x60;;&#x60; character. Duplicate directives will be merged with later directives in the array being appended to earlier ones.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


