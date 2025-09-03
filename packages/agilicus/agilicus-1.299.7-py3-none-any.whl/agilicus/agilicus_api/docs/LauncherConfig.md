# LauncherConfig

The configuration for a Launcher to be installed on the host computer. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**command_path** | **str** | The application full path and name, located on the host computer. | [optional] 
**command_arguments** | **str** | The arguments necessary for the command to run. | [optional] 
**start_in** | **str** | The launcher start directory | [optional] 
**interceptor_config** | [**InterceptorConfig**](InterceptorConfig.md) |  | [optional] 
**do_intercept** | **bool** | If the launcher command requires the use of an interceptor. | [optional]  if omitted the server will use the default value of True
**http_share_port** | **int** | If configured the launcher will provide local http access to shares attached to this launcher. They will be made available at http://localhost:&lt;port&gt;/org-id/share-name.  | [optional] 
**hide_console** | **bool** | If proxify should use \&quot;--no-console\&quot; | [optional]  if omitted the server will use the default value of False
**disable_http_proxy** | **bool** | If proxify should disable the default http_proxy. This controls the proxify command invocation of \&quot;--no-http-proxy\&quot;  | [optional]  if omitted the server will use the default value of False
**run_as_admin** | **bool** | When true, the launcher will run elevated as administrator.  | [optional] 
**extra_processes** | [**[ExtraProcess]**](ExtraProcess.md) | A set of out of process tasks which will be attached by the interceptor that are not part of the program&#39;s process tree. Eg: - Background services - Side-processes started using a messaging protocol  | [optional] 
**end_existing_if_running** | **bool** | When true, allows ending the existing running program during a launch  | [optional]  if omitted the server will use the default value of False
**wait_for_all_descendants** | **bool** | When true in non-interception mode, the launcher continues to run until all descendants of the spawned process have terminated. Use this if the launched application is itself a launcher for something else -- i.e. it spawns the main application then exits. In such cases, you want the launcher to continue to run so that it can proxy requests for the main application and any of its descendants.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


