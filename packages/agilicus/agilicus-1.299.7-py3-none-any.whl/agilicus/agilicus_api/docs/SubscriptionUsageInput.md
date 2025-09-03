# SubscriptionUsageInput

Information about the number of things used by a subscription. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**num_resources** | **int** | The number of resources. Broken out separately both for convenience, but also to ensure that constraints involving the number of resources take into account unknown resource types potentially added in the future.  | [optional] 
**num_desktops** | **int** | The number of desktops. | [optional] 
**num_applications** | **int** | The number of applications. | [optional] 
**num_networks** | **int** | The number of networks. | [optional] 
**num_ssh** | **int** | The number of ssh resources. | [optional] 
**num_databases** | **int** | The number of databases. | [optional] 
**num_resource_groups** | **int** | The number of resource groups. | [optional] 
**num_fileshares** | **int** | The number of fileshares. | [optional] 
**num_launchers** | **int** | The number of launchers. | [optional] 
**num_users** | **int** | The number of users. | [optional] 
**num_groups** | **int** | The number of groups. | [optional] 
**num_orgs** | **int** | The number of organistions in the subscription. | [optional] 
**num_connectors** | **int** | The number of connectors in the subscription. | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


