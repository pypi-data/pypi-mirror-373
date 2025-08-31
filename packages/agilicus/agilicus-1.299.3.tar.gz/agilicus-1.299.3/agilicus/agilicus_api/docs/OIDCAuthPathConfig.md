# OIDCAuthPathConfig

The configuration of included_paths and excluded_paths that will be used for authentication. Paths in included_paths will require user authentication before allowing access, Paths in excluded_paths will allow access without user authentication. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**included_paths** | [**[OIDCAuthURI]**](OIDCAuthURI.md) | A list of paths that will require the user to have authenticated before allowing access. If this list is unset, all paths will require authentication.  | [optional] 
**excluded_paths** | [**[OIDCAuthURI]**](OIDCAuthURI.md) | A list of paths that allow user access without authentication. If the included_paths are not set, all paths except paths in excluded_paths require authentication before allowing access  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


