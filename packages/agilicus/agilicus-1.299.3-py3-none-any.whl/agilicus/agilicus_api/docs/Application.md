# Application

Application's properties

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | application name | 
**category** | **str** | application category | 
**org_id** | **str** | organisation id | 
**created** | **datetime** | Creation time | [optional] [readonly] 
**id** | **str** | application service id | [optional] [readonly] 
**parent_id** | **str** | For inheritance, defines the parent id. | [optional] [readonly] 
**description** | **str** | Application description text | [optional] 
**image** | **str** | image registry path and name | [optional] 
**image_username** | **str** | registry username | [optional] 
**image_password** | **str** | registry password | [optional] 
**image_credentials_type** | **str** | type of credentials for image | [optional] 
**environments** | [**[Environment]**](Environment.md) | List of environments | [optional] 
**contact_email** | **str** | Administrator contact email | [optional] 
**monitoring_config** | [**ApplicationMonitoringConfig**](ApplicationMonitoringConfig.md) |  | [optional] 
**port** | **int** | The transport layer port the application listens on for requests. E.g. if the application listens for HTTP requests on the standard port, port 80, set this to 80.  | [optional] 
**healthcheck_uri** | **str** | health check URI | [optional] 
**roles** | [**RoleList**](RoleList.md) |  | [optional] 
**roles_config** | [**RolesConfig**](RolesConfig.md) |  | [optional] 
**rules_config** | [**RulesConfig**](RulesConfig.md) |  | [optional] 
**definitions** | [**[Definition]**](Definition.md) | List of definitions | [optional] 
**assignments** | [**[ApplicationAssignment]**](ApplicationAssignment.md) | Controls the Organisations which have access to Environments of this Application.  | [optional] 
**owned** | **bool** | Whether this Application is owned by the provided organisation.  | [optional] 
**maintained** | **bool** | Whether this Application has an Environment maintained by the provided organisation.  | [optional] 
**assigned** | **bool** | Whether an Environment is assigned to this Application.  | [optional] 
**published** | **str** | Whether or not this Application is published, and if so, how. An application that has been published somewhere will have high level details about it visible (through apis intended to expose published applications), such as its name and description. The enum values mean the following:  - no: This application is not published. It will only be visibile to users with       permission to access the application, or to administrators.  - public: This application is published to the public catalogue. Any user who       can request access to the organisation will see high level details about this       application.  | [optional]  if omitted the server will use the default value of "no"
**default_role_id** | **str, none_type** | The id of the default role to use for this application. This role will be assigned to users granted access to this application by default, unless overridden. This value must point to a valid Role for this application. A string of length 0 will clear out the default role. | [optional] 
**default_role_name** | **str, none_type** | The name of the default role. Does not change which role is used. Provided for convenience.  | [optional] [readonly] 
**icon_url** | **str** | A url pointing to an icon representing this application.  | [optional] 
**display_info** | [**DisplayInfo**](DisplayInfo.md) |  | [optional] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**location** | **str** | Where the application runs. Applications can run within an Agilicus hosting platform, or elsewhere on the internet. The possible values have the following meanings:   - &#x60;hosted&#x60;: the application runs on the Agilicus hosting platform.   - &#x60;external&#x60;: the application runs elsewhere on the internet. External applications     will not create instances in the Agilicus hosting platform. However, they will     be able to use Agilicus for Identity and Authentication.  | [optional] 
**service_account_id** | **str** | Service account user GUID used to deploy the application | [optional] [readonly] 
**service_account_required** | **bool** | If service_account_enabled field is set to true, a service account will be created. If service_account_enabled field is set to false, the service account will be deleted. If the service_account_enabled field is not set no action on the service account is taken.  | [optional] 
**application_type** | **str** | The type of application meanings:   - &#x60;user_defined&#x60;: A user defined application.   - &#x60;internal&#x60;: An internal application used by agilicus services.  | [optional]  if omitted the server will use the default value of "user_defined"
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**workload_config** | [**WorkloadConfiguration**](WorkloadConfiguration.md) |  | [optional] 
**admin_state** | [**ApplicationStateSelector**](ApplicationStateSelector.md) |  | [optional] 
**alternate_mode_setting** | [**AlternateModeSetting**](AlternateModeSetting.md) |  | [optional] 
**launchers** | **[str]** | A list of launchers that can be used to launch this application.  | [optional] 
**parent_name** | **str** | If an application inherits from a parent application (when parent_id exists), this property provides the name of the parent.  | [optional] [readonly] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


