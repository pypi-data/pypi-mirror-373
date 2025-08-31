# FileShareServiceSpec

The configurable properties of a FileShareService. Since multiple file shares will be exposed using the same host, no two FileShareServices in the same organisation may have the same share_name. The connector_id controls which connector will be used to expose this file share. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the service. This uniquely identifies the service within the organisation.  | 
**share_name** | **str** | The name of the share as exposed to the Internet. This will be used to build the URI used to mount the share. The share_name is unique among the file shares of the organisation.  | 
**org_id** | **str** | Unique identifier | 
**local_path** | **str** | The path to the directory to share on the local file system. This should point to a directory, not a file. Use a slash (&#39;/&#39;, U+002F) to separate directories within the path.  | 
**connector_id** | **str** | Unique identifier | 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**share_index** | **int** | The index of the FileShareService. This is used to construct a unique URI at which to access this FileShareService.  | [optional] 
**transport_end_to_end_tls** | **bool** | Whether or not the FileShareService encrypts data using the same Transport Layer Security (TLS) session as seen by the client. Setting this to true will cause the FileShareService to provision a Certificate signed by a private key only known to it. All traffic to and from the FileShareService will be encrypted using a TLS session derived from that Certificate. Setting this to false will cause the FileShareService to use a TLS session derived from a Certificate provisioned by the Agilicus Cloud.  | [optional] 
**transport_base_domain** | **str** | The base domain from which to access this share. The file share endpoint will be \&quot;https://share-$(share_index).$(base_domain)\&quot;  | [optional] 
**file_level_access_permissions** | **bool** | Enable file acl permissions on the agent&#39;s host. This option enables fine grained control of individual files based on a user&#39;s specific groups and access level  | [optional]  if omitted the server will use the default value of False
**client_config** | [**[NetworkMountRuleConfig]**](NetworkMountRuleConfig.md) | The configuration to determine where this share should be used automatically. Use this field to set up clients to mount a share automatically.  | [optional] 
**resource_config** | [**ResourceConfig**](ResourceConfig.md) |  | [optional] 
**sub_path** | **str** | The subpath extending the local file system which is being shared, supporting vars expansion | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


