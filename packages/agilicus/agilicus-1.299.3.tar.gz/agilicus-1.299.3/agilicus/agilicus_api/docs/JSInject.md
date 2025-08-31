# JSInject

Enable javascript injection and provide the location or script to load.  The code will be injected prior to the `</head>` in the main asset loading of the root page. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**script_name** | **str** | The name of the script that will be loaded.  | [optional] 
**sri_hash** | **str** | The SubResource Integrity (SRI) hash of the inject_script.  | [optional] [readonly] 
**inject_script** | **str, none_type** | The injected script to be called from the root page. Note this can be generated automatically using an inject_preset option, or using a manually set script. This property cannot be set (and will be ignored), if the inject_preset option is set.  | [optional] 
**inject_preset** | **str, none_type** | A predefined inject type.  possible values:    &#39;set-cookie-for-service-routes&#39;:       A js script that will iterate over all service routes (see ApplicationServiceRoute) that       have property set_token_cookie set to True, and set their cookie according to the external_name       that is set for its service route.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


