# KerberosUpstreamStatusKeyTabEntries


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**principal** | **str** | The principal for this keytab entry. Must be of the form \&quot;auth.&lt;your-domain&gt;@YOURORG.COM\&quot;  | [optional] 
**timestamp** | **datetime** | Update time | [optional] 
**key_type** | **str** | Kerberos encryption type, see https://www.iana.org/assignments/kerberos-parameters/kerberos-parameters.xhtml  | [optional] 
**kvno** | **int** | The generation of this keytab entry, encremented each time a key is generated  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


