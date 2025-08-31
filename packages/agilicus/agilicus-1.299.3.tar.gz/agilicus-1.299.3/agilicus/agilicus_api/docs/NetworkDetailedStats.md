# NetworkDetailedStats

Detailed network statistics 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**connections_current** | **int** | The total number of connections currently established or establishing. This value is a guage, meaning it is not monotonic.  | 
**connections_timedout** | **int** | The number of times a connection attempt failed because it took too long to establish | 
**connections_host_not_found** | **int** | The number of times a connection attempt failed because a host lookup failed | 
**connections_reset** | **int** | The number of times a connection attempt failed because the target host reset the connection  | 
**connections_tls_validation_failed** | **int** | The number of times a connection attempt failed because TLS validation did not succeed. This is typically because either the server certificate did not match the expected one, or because we did not trust it. Try to fix this problem by ensuring that the certitifate is valid, matches the hostname the client connects to, and that it is issued by a certificate authority trusted by the client. Alternatively, if this is not possible, disable certificate validation.  | 
**connections_other_failure** | **int** | The number of times a connection attempt failed for reasons other than the explicitly enumerated ones.  | 
**connections_tls_protocol_failure** | **int** | The number of times a connection attempt failed because the upstream returned an invalid TLS response. Typically this happens because the upstream is not configured to use TLS, but it could be due to a bug in the upstream server, or some other incompatibility (e.g. an unsupported version whose versioning mechanism is unknown). Check that the server is configured to serve TLS, or connect to it using plaintext.  | [optional] 
**connections_tls_unsupported_version** | **int** | The number of times a connection attempt failed because the upstream server replied that it did not support one of the versions supported by the client. Typically this is because the server is running a fairly old version of software. See if there is a new version of the software available, or ensure that it provides a maximum TLS version of at least 1.2.  | [optional] 
**connections_tls_remote_error** | **int** | The number of times a connection attempt failed because the upstream server replied that it was unable to accept the connection request. This can be for various reasons such as an incompatible set of cipher suites. Check that the server supports a modern set of cipher suites, or look at its logs to see if it indicates the reason for the failure.  | [optional] 
**connections_tls_other_error** | **int** | The number of times a connection attempt failed because the TLS negotiation failed for reasons other than the explicitly enumerated ones.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


