# HostPrefixRuleCondition

Matches the host and prefix of an HTTP request. The host will normalize the port-part for standard schemes. `http://` normalises to port 80. `https://` normalises to port 443. For example, with   host: example.com   prefix: /absolute/path The following URLs will match:   http://example.com/absolute/path   http://example.com/absolute/path/subpath   http://example.com:80/absolute/path/subpath The following URLs will *not* match:   http://example2.com/absolute/path   http://example.com/absolute/other   http://example.com:8080/absolute/path    Note in particular, http://example.com:80/absolute/path matches because port 80 is the   standard http port, whereas http://example.com:8080/absolute/path does *not* match, because   8080 is not the standard http port. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition_type** | **str** | The discriminator for the condition | 
**host** | **str** | A case insensitive host or IP address, possibly including a port. Note that if the host is an empty string, then it s considered a trivial match.  | 
**prefix** | **str** | A case-sensitive, absolute prefix to match against. The prefix cannot contain a query string.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


