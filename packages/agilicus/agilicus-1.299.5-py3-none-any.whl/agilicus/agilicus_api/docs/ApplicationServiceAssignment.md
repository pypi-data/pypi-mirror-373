# ApplicationServiceAssignment

An ApplicationServiceAssignment allows an Environment of an Application to access an ApplicationService. Essentially, ApplicationSerivceAssignment models a link between an Environment and an ApplicationService. For example, a collection of these with the same Environment would model the set of ApplicationServices that environment can access. Alternatively, a collection of these with the same ApplicationService would model the set of Environments that can access that ApplicationService. ApplicationServiceAssignments apply to the Organisation of the ApplicationService being assigned. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**app_id** | **str** | The identifier of the Application to which this service is being assigned.  | 
**environment_name** | **str** | The name of the Environment to which this ApplicationService is being assigned.  | 
**org_id** | **str** | The organisation owning the Application to which the ApplicationService is being assigned.  | 
**expose_type** | **str** | A service can be exposed via the following ways: &#39;application&#39;:     A service assigned to an application will be exposed externally as that application. This     sets up an ingress route that forwards from the applications FQDN to this service. This property     can only be true for one service bound to an application and environment. If the environment     has domain_aliases, those alises would also expose this service. &#39;path_prefix&#39;:     This setting exposes the service as a path prefix to the applications hostname.  The generated     prefix would be constructed as: {service_name}_{port} &#39;hostname&#39;:     exposes the service as a specific hostname(s), as provisioned by the expose_as_hostnames property &#39;not_exposed&#39;:     The service is not externally exposed.  | [optional]  if omitted the server will use the default value of "not_exposed"
**expose_as_hostnames** | [**[Domain]**](Domain.md) | If expose_type is set to hostname, this list allows additional hostnames to be used to map to this service.  | [optional] 
**load_balancing** | [**ApplicationServiceLoadBalancing**](ApplicationServiceLoadBalancing.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


