# ApplicationServiceRoute

An application service route defines how a service, which is associated to an application, is routed internally. This would be based upon how the service is assigned (the ApplicationServiceAssignment), and its expose_type.  For a service route, it is expected that an external name and/or path_prefix would route to an internal_name.  Hosted applications, where assets are served locally by the application itself (rather than to an upstream service), may also have a service route(s). If there are domain aliases configured for the Application, there would be a unique ApplicationServiceRoute for each domain alias for that application, however no service_id will be present since one does not exist.  Examples:     external_name -> internal_name     external_name/path_prefix -> internal_name     application_external_name/path_prefix -> internal_name 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**expose_type** | **str** | A service can be exposed via the following ways: &#39;application&#39;:     A service assigned to an application will be exposed externally as that application. This     sets up an ingress route that forwards from the applications FQDN to this service. This property     can only be true for one service bound to an application and environment. If the environment     has domain_aliases, those alises would also expose this service. &#39;path_prefix&#39;:     This setting exposes the service as a path prefix to the applications hostname.  The generated     prefix would be constructed as: {service_name}_{port} &#39;hostname&#39;:     exposes the service as a specific hostname(s), as provisioned by the expose_as_hostnames property &#39;not_exposed&#39;:     The service is not externally exposed.  | defaults to "not_exposed"
**service_id** | **str** | Unique identifier | [optional] [readonly] 
**protocol_config** | [**ServiceProtocolConfig**](ServiceProtocolConfig.md) |  | [optional] 
**path_prefix** | **str** | The URL path prefix should service routing be achieved by using a path prefix.  | [optional] 
**internal_name** | **str** | The internal name of the service.  | [optional] 
**external_name** | **str** | The external name of the service. If the field is nullable or an empty string, then the external name of the service is implied to be the external name of the application.  | [optional] 
**load_balancing** | [**ApplicationServiceLoadBalancing**](ApplicationServiceLoadBalancing.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


