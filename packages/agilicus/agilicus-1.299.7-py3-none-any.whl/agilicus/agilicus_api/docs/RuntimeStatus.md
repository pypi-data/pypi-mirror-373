# RuntimeStatus

The details about the current running status of an instance. This information allows a user to get information about the running software in the Agilicus Portal. For example, you can check an upgrades status, check for downed instances or troubleshoot poor performance. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**overall_status** | **str** | The status of the running components. - A &#x60;good&#x60; status means that no action is neccessary on this environment - A &#x60;warn&#x60; status means that there is an issue that should be dealt with   Examples include a rollout failing or crashing containers - A &#x60;down&#x60; status indicates that there is a service accessibility problem   that should be dealt with as soon as possible. This could   mean that there were multiple failed rollouts, containers are unstable,   access to a neccessary service is down or other problems. - A &#x60;stale&#x60; status indicates that although there may not be anything wrong,   we haven&#39;t been able to update the status recently. This may indicate   an issue with the platform - A &#x60;degraded&#x60; status indicates that the service is operational but running   in non-redundant mode. Note that this alarm would only be valid for   a service that supports redundancy.  | [optional] 
**running_replicas** | **int** | The number of current running replicas. 2 is redundant, 1 could indicate error handling, 0 is down.  | [optional] 
**error_message** | **str** | The error in running the current instance. Common errors include CrashLoopBackoff, ContainerPullError, ConfigError. If there is no error description, this will be empty.  | [optional] 
**restarts** | **int** | How many times a container has restarted across all replicas of this instance. A non-zero number might indicate some intermittent error that is handled by the Agilicus system. A large number of errors could indicate problems in the application  | [optional] 
**cpu** | **float** | The current number of CPU cores used by all the containers for the instance. A high number eg 1.00 may indicate performance problems as a container is unable to service all requests  | [optional] 
**memory** | **float** | The amount of RAM used by all containers used for the instance in MiB  | [optional] 
**last_apply_time** | **datetime** | The last time any change was applied to the running containers. This can be used to indicate if the system has &#39;picked up&#39; a recent change that was made  | [optional] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**running_image** | **str** | The container tag identifies what container is currently running in this instance. This could be different than the configured image if there was an error upgrading. Although relatively rare in practice, the same image tag could have been pushed with many different images, when the container is started it will pull the latest version. See running_hash for more information  | [optional] 
**running_hash** | **str** | The container hash of What versions users see when they browse to the site. If a image tag has been pushed multiple times, ie for hotfixes then this could be used to identify exactly what software is running  | [optional] 
**org_id** | **str** | Unique identifier | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


