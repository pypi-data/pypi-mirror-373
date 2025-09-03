# ExtraProcess

A specification for an extra process to track outside of the main processes' life cycle 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**program_name** | **str** | Full path to the process to run or attach to | 
**name_regex_flag** | **bool** | If set use program name as a regex for finding the process to attach to by name or executable path can&#39;t be set if start_if_not_running is set.  | [optional]  if omitted the server will use the default value of False
**start_if_not_running** | **bool** | If there isn&#39;t a process running this service when running the launcher start it  | [optional]  if omitted the server will use the default value of False
**exit_when_ending** | **bool** | If the process should be terminated when the launcher exits  | [optional]  if omitted the server will use the default value of True
**attach_if_already_running** | **bool** | If the process is already running when the launcher starts, attach to it an intercept its traffic  | [optional]  if omitted the server will use the default value of False
**fork_then_attach** | **bool** | Some programs require specific startup initialization procedures that cause the initial interceptor spawn + resume startup procedure to not function correctly. The typical behavior for this type of program is exhibited as the program terminates prematurely. This setting, when true, does a normal fork and will attach to the pid after the process has initially started. | [optional]  if omitted the server will use the default value of False
**command_arguments** | **str** | The arguments necessary for the command to run. | [optional] 
**start_in** | **str** | The directory this extra process will start in | [optional] 
**match_arguments** | **bool** | When attaching to a running process, match on both the process and the arguments | [optional] 
**wait_for_exit** | **bool** | When running the interceptor, wait on this proccess as well as the main process. You can use this with the process name to intercept processes that call some kind of launcher which runs another process.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


