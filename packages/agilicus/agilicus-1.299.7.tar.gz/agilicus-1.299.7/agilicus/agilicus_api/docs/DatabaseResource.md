# DatabaseResource

A Database exposed via the Agilicus Cloud. Access the machine using a client supporting the chosen database protocol. A Connector provides connectivity between the Agilicus Cloud and your database so that you do not have to expose it to the the Internet. The connector performs client authorization using the credentials (e.g. username/password being an API Key) provided by the client, ultimately using the permissions of the associated user to decide whether to allow the connection to the database. The connector authenticates itself to the database by using credentials stored in the Credentials API.  The client connections run over TLS, using a domain name unique to the DatabaseResource for routing. The connector terminates these TLS connections. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**DatabaseResourceSpec**](DatabaseResourceSpec.md) |  | 
**metadata** | [**MetadataWithId**](MetadataWithId.md) |  | [optional] 
**status** | [**DatabaseResourceStatus**](DatabaseResourceStatus.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


