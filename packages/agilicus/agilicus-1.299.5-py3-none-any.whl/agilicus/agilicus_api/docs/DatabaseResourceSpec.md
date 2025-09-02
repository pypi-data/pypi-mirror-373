# DatabaseResourceSpec

The configurable properties of a DatabaseResource. A DatabaseResource is also a NetworkResource, so it must have a unique name across all NetworkResources. Note that the DatabaseResource must be associated with a Connector (via `connector_id`) in order for users to access it. If `connector_id` is empty, then the DatabaseResource cannot be accessed. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the DatabaseResource. This uniquely identifies the DatabaseResource within the organisation. It is used to build the domain name for the resource, so it must be a valid hostname.  | 
**address** | **str** | The hostname or IP of the DatabaseResource. The associated connector will proxy connections to the DatabaseResource&#39;s domain to this address.  | 
**database_protocol** | **str** | The protocol of this database. The DatabaseResource will not translate between two different protocols, so both the client and server must use this protocol when communicating.  The DatabaseResource currently supports the following protocols:   - postgresql: The PostgreSQL database wire protocol, version 3.  | 
**data_source_name** | **str** | The name of the database to connect to. This will be used when first connecting to the database so that you know you&#39;re accessing the right data. If provided, this will override the name of the database provided by the client.  | 
**org_id** | **str** | Unique identifier | 
**runtime_parameters** | **[str]** | Extra runtime parameters which can override or extend the ones applied by the client. These will be serialized into the upstream connection depending on the version of the protocol.  | [optional] 
**config** | [**NetworkServiceConfig**](NetworkServiceConfig.md) |  | [optional] 
**connector_id** | **str** | Unique identifier | [optional] 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**resource_config** | [**ResourceConfig**](ResourceConfig.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


