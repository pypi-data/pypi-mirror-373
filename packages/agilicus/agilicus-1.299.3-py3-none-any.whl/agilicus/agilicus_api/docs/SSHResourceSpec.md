# SSHResourceSpec

The configurable properties of a SSHResource. A SSHResource is also a NetworkResource, so it must have a unique name across all NetworkResources. Note that the SSHResource must be associated with a Connector (via `connector_id`) in order for users to access it. If `connector_id` is empty, then the SSHResource cannot be accessed. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the SSHResource. This uniquely identifies the SSHResource within the organisation.  | 
**address** | **str** | The hostname or IP of the SSHResource. A terminal emulator will proxy requests from the machine through to this address via the Connector associated with this gateway using &#x60;connector_id&#x60;.  | 
**org_id** | **str** | Unique identifier | 
**username** | [**SSHUsername**](SSHUsername.md) |  | [optional] 
**config** | [**NetworkServiceConfig**](NetworkServiceConfig.md) |  | [optional] 
**connector_id** | **str** | Unique identifier | [optional] 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**resource_config** | [**ResourceConfig**](ResourceConfig.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


