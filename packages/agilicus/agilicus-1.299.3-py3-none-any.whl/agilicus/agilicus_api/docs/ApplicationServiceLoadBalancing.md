# ApplicationServiceLoadBalancing

Configure how the system load balances to an application service. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connection_mapping** | **str** | How to map downstream connections to this request to upstream connections.   - &#x60;one-to-one&#x60;: Each downstream connection corresponds to exactly one upstream connection.     This can be quite useful when using http in conjuction with NTLM or Negotiate     authentication. However, it does place more load on the connector: it must maintain     a single connection for every upstream connection, meaning that it cannot rely on connection     pooling to optimize communication with the upstream.  - &#x60;default&#x60;: fall back on the default connection pooling behaviour. This may be overriden by other     configuration. For example, NTLM passthrough requires one-to-one connectivity. If the connection mapping     is configured as \&quot;default\&quot;, then the connector will choose to use one-to-one connectivity.  | defaults to "default"
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


