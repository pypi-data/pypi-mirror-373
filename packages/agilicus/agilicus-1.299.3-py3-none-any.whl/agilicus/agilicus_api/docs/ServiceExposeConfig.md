# ServiceExposeConfig

Configuration related to exposing a Network Service. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**expose_as_hostname** | **bool** | Exposes the network as a TLS endpoint. This is suitable for Networks that require direct access to a Network Service that supports TLS. This requires that the client must set the SNI in the TLS hello according to the hostname naming scheme:    &lt;service_name&gt;.networks.&lt;organisation subdomain&gt;  When enabled, for convenience, the hostname for the exposed network service is provided in the ApplicationServiceRoutingInfo in the exposed_as_hostname property.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


