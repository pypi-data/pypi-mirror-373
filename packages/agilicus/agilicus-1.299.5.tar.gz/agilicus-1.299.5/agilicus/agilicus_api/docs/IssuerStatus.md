# IssuerStatus

The read-only, inferred properties of the issuer. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**theme_file_id** | **str** | ID of the theme file. The theme file is a zip file containing the web assets to show the client on login. | [optional] 
**operational_status** | [**OperationalStatus**](OperationalStatus.md) |  | [optional] 
**trusted_issuers** | [**[TrustedIssuer]**](TrustedIssuer.md) | The list of trusted issuers for federated login.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


