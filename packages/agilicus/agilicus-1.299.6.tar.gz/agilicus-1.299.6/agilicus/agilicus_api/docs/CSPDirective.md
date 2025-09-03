# CSPDirective

A CSPDirective forms the core of a Content Security Policy (CSP). The policy is a series of directives which each control different aspects of how an Application accesses content. The `name` field defines the meaning of the directive; it is interpreted by the browser according to the browser's implementation of CSP. The list of values describes the behaviour of the particular directive. When rendered into the `Content-Security-Policy` header, the directive will take the form: `{name} {values[0]} {values[1]} ... {values[n]}`. That is, it starts with the `name`, followed by the list of values joined by spaces.  See https://www.w3.org/TR/CSP2/ for the details of the CSP standard. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The directive controlling the CSP. This value has meaning according to the CSP standard and the browser&#39;s implementation of it.  | 
**values** | **[str]** | The values describing the behaviour of the directive. This array may be empty. Note that whether or not the directive is surrounded by single quotes (\&quot;&#39;\&quot;) is important to the meaning of the policy. For example, &#x60;&#39;self&#39;&#x60; has special meaning, whereas &#x60;self&#x60; will likely be considered as a URI.  | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


