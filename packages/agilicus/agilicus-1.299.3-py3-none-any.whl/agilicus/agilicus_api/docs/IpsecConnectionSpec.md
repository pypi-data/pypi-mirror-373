# IpsecConnectionSpec

An IPsec specification for a connection. A connection is made from Agilicus cloud (local) to the customer (remote). 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ike_version** | **str** | The IKE version | [optional] 
**remote_ipv4_address** | **str** | remote peer IPv4 address | [optional] 
**remote_dns_ipv4_address** | **str** | remote peer DNS IPv4 address | [optional] 
**remote_healthcheck_ipv4_address** | **str** | Remote peer healthcheck IPv4 address. The remote peer address must respond to ping (ICMP). This is used to validate the health of the connection.  | [optional] 
**ike_cipher_encryption_algorithm** | [**CipherEncryptionAlgorithm**](CipherEncryptionAlgorithm.md) |  | [optional] 
**ike_cipher_integrity_algorithm** | [**CipherIntegrityAlgorithm**](CipherIntegrityAlgorithm.md) |  | [optional] 
**ike_cipher_diffie_hellman_group** | [**CipherDiffieHellmanGroup**](CipherDiffieHellmanGroup.md) |  | [optional] 
**esp_cipher_encryption_algorithm** | [**CipherEncryptionAlgorithm**](CipherEncryptionAlgorithm.md) |  | [optional] 
**esp_cipher_integrity_algorithm** | [**CipherIntegrityAlgorithm**](CipherIntegrityAlgorithm.md) |  | [optional] 
**esp_cipher_diffie_hellman_group** | [**CipherDiffieHellmanGroup**](CipherDiffieHellmanGroup.md) |  | [optional] 
**esp_lifetime** | **int** | Absolute time after which an IPsec security association expires, in minutes.  | [optional] 
**ike_lifetime** | **int** | Absolute time after which an IKE security association expires, in minutes.  | [optional] 
**ike_rekey** | **bool** | Allows control of IKE rekey. true is enabled, false is disabled.  | [optional] 
**ike_reauth** | **bool** | Allows control of IKE re-authentication. true is enabled, false is disabled.  | [optional] 
**ike_authentication_type** | **str** | The IKE authentication type. | [optional] 
**ike_preshared_key** | **str** | ike preshared key | [optional] 
**ike_chain_of_trust_certificates** | **str** | Chain of trust certficates. Certificates are PEM encoded and are separated by a newline.  ie. A signed by B would be a string where A is first, newline, followed by B.  | [optional] 
**ike_certificate_dn** | **str** | certificate distinguished name (DN) Deprecated in favour of the generic ike_remote_identity field.  | [optional] 
**ike_remote_identity** | **str** | The identity of the remote peer. The remote peer will send credentials including this identity as part of the IKE authentication exchange.  The meaning of the identity depends on the authentication type.   - &#x60;ike_preshared_key&#x60;: This is an arbitrary value provisioned on the remote     peer, often a FQDN or email address. E.g. \&quot;vpn.my-org.example.com\&quot;.   - &#x60;certificate&#x60;: This is the distinguished name (DN) of the entity certificate     presented by the remote peer. E.g. \&quot;C&#x3D;CA; O&#x3D;Agilicus; CN&#x3D;vpn-1.ca-1.agilicus.ca\&quot;.  | [optional] 
**local_ipv4_block** | **str** | The local IP block that used by the tunnel. A tunnel requires a /30 subnet, within the following IP address ranges    192.168.0.0 -&gt; 192.168.255.252   172.16.0.0 -&gt; 172.31.255.255  | [optional] 
**remote_ipv4_ranges** | [**[IpsecConnectionIpv4Block]**](IpsecConnectionIpv4Block.md) | One or more IP address ranges that define the peer network range.  | [optional] 
**use_cert_hash** | **bool** | Controls if certificate exchange using hash is enabled.  | [optional] 
**local_certificate_uribase** | **str** | Provides the local endpoint uri base for certificate hash lookup. See https://tools.ietf.org/html/rfc7296#section-3.6 (Hash and URL encoding). Note that since the ultimate URL is constructed through concatenation, the final &#x60;/&#x60; is important.  | [optional] 
**remote_certificate_uribase** | **str** | Provides the remote endpoint uri base for certificate hash lookup. See https://tools.ietf.org/html/rfc7296#section-3.6 (Hash and URL encoding). Note that since the ultimate URL is constructed through concatenation, the final &#x60;/&#x60; is important.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


