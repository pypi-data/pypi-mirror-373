# DesktopResourceSpec

The configurable properties of a DesktopResource. A DesktopResource is also a NetworkResource, so it must have a unique name across all NetworkResources. Note that if the DesktopResource must be associated with a Connector (via `connector_id`) in order for users to access it. If `connector_id` is empty, then the DesktopResource cannot be accessed. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | The name of the DesktopResource. This uniquely identifies the DesktopResource within the organisation.  | 
**address** | **str** | The hostname or IP of the DesktopResource. A Desktop Gateway will proxy requests from the client through to this address via the Connector associated with this gateway using &#x60;connector_id&#x60;.  | 
**desktop_type** | **str** | The type of desktop represented by this DesktopResource. The type identifies which protocol will be used to communicate with it. The possible types are:   - &#x60;rdp&#x60;: Remote Desktop Protocol (RDP). This allows clients which support RDP to connect to a desktop     running an RDP server.   - &#39;vnc&#39;: Virtual Network Computing protocol (VNC). This allows the clients that support VNC to connect to a     desktop running a VNC server  | 
**org_id** | **str** | Unique identifier | 
**config** | [**NetworkServiceConfig**](NetworkServiceConfig.md) |  | [optional] 
**session_type** | **str** | The internal session type. In Microsoft Remote Desktop, &#x60;admin&#x60; means console.   - &#x60;admin&#x60;: Connect to the console (session id &#x3D; 0)   - &#x60;user&#x60;: Create a new user session, which might sign out the console depending on setup.  | [optional]  if omitted the server will use the default value of "user"
**connector_id** | **str** | Unique identifier | [optional] 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**connection_info** | [**DesktopConnectionInfo**](DesktopConnectionInfo.md) |  | [optional] 
**remote_app** | [**DesktopRemoteApp**](DesktopRemoteApp.md) |  | [optional] 
**extra_configs** | **[str]** | Extra configuration for desktops. For RDP desktops use https://learn.microsoft.com/en-us/azure/virtual-desktop/rdp-properties These fields will be added to the end of the generated RDP configuration files. These configurations will override other configurations.  | [optional] 
**resource_config** | [**ResourceConfig**](ResourceConfig.md) |  | [optional] 
**allow_non_domain_joined_users** | **bool** | Whether to allow non-domian-joined users. If true, append relavant properties for user&#39;s RDP session  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


