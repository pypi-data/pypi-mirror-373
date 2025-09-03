# Environment

Environment's properties

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Environment name | 
**created** | **datetime** | Creation time | [optional] [readonly] 
**maintenance_org_id** | **str** | The Organisation which is responsibile for maintaining this Environment. Often this will be the same Organisation as the owning Application. However, sometimes it makes sense to delegate this responsibility to another Organisation. To do so, set this field to that Organisation&#39;s identifier. Users with sufficient permissions in that organisation will be able to modify this Environment. If the maintenance_org_id is not provided, it will populated with that of the parent application&#39;s organisation.  | [optional] 
**domain_aliases** | **[str]** | A list of alternative domains for an instance. This can be used if you want to use a different FQDN for your application instead of the default &#x60;appname.org_subdomain&#x60;. Multiple different names can be useful if an application is multi-tenant, that is it can be accessed by multiple organisations and you don&#39;t want your users to see it any different to existing web applications. A certificate will be generated for all valid domains. All aliases entered must have a cname assignment pointing to the FQDN of the cluster hosting your application.  | [optional] 
**version_tag** | **str** | The version of the container to run. Required if the owning application is hosted.  | [optional] 
**config_mount_path** | **str** | config_as_mount file path | [optional] 
**config_as_mount** | **str** | A json object of config applied as file mounted | [optional] 
**config_as_env** | **str** | A json object of config applied as environment | [optional] 
**secrets_mount_path** | **str** | secret_as_mount file path | [optional] 
**secrets_as_mount** | **str** | A json object of secrets applied as file mounted | [optional] 
**secrets_as_env** | **str** | A json object of secrets applied as environment | [optional] 
**application_services** | [**[ApplicationService]**](ApplicationService.md) | The services used by the application for this environment. Note that in order to add a service to the environment, this environment must be added to the list of assignments for that service in the ApplicationService collection for the organisation.  | [optional] [readonly] 
**serverless_image** | **str** | serverless image path | [optional] 
**status** | [**EnvironmentStatus**](EnvironmentStatus.md) |  | [optional] 
**updated** | **datetime** | Update time | [optional] [readonly] 
**application_configs** | [**ApplicationConfig**](ApplicationConfig.md) |  | [optional] 
**scopes** | **[str]** | A list of scopes to be requested on behalf of the user of the application and as well as configured based on the application launchers that launch this application/environment. This field is only populated on a GET request when the query parameter get_scopes&#x3D;True is passed.  | [optional] [readonly] 
**name_slug** | [**K8sSlug**](K8sSlug.md) |  | [optional] 
**migrated_app_id** | **str** | Environments are in transition to be deprecated. When an environment is migrated, an application is created specific for the environment. This property provides the id of the application that this environment has been migrated to.  | [optional] 
**proxy_location** | **str** | If this application is a simple Web Application Firewall proxy, this field controls where the proxy runs. The possible values have the following meanings:  - &#x60;in_cloud&#x60;. An application which is &#x60;in_cloud&#x60; runs the proxy in the Agilicus cloud. This means that the application&#39;s data will be decrypted in the Agilicus cloud so that the proxy may perform authentication, authorization, sanitisiation and modification tasks prior to forwarding the request to the destination service. - &#x60;on_site&#x60;: An application which is &#x60;on_site&#x60; runs the proxy as part of an AgentConnector located on a machine run by you. The application&#39;s data is not decrypted until it reaches that machine. Any secrets required to do this (such as private keys for TLS Certificates) stay on that machine; they are never transmitted to Agilicus. The proxy running on site will decrypt the data, and perform authentication, authorisation and modification tasks prior to forwarding the request to the destination service.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


