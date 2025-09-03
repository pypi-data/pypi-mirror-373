# DesktopRemoteApp

Provisions a RemoteApp. Users connecting using this DesktopResource will launch the given application upon connection using the appropriate protocol for launching applications associated with the desktop_type. Note that not all fields will be used, depending on the desktop_type.  If the desktop_type does not support a remote_app protocol, then this field must be left undefined.  If this field is set to None on an existing DesktopResource, the RemoteApp will be removed; the Desktop will revert back to full Desktop access. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**command_path** | **str** | The full path and name to the remote application&#39;s executable on the machine  | 
**command_arguments** | **str** | The arguments to the command. | [optional] 
**working_directory** | **str** | The directory to start the application in. | [optional] 
**expand_command_line_with_local** | **bool** | Whether to expand environment variables in the command arguments using local values. If false, uses the remote system&#39;s environment variables.  | [optional] 
**expand_working_directory_with_local** | **bool** | Whether to expand environment variables in the working directory using local values. If false, uses the remote system&#39;s environment variables.  | [optional] 
**file_to_open** | **str** | The file, if any, to be opened on the remote desktop by the remote app.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


