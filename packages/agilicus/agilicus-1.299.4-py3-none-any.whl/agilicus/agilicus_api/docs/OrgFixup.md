# OrgFixup

An Organisation fixup is sometimes required if during an org create, components may have failed, such as upstream billing config, etc. This object allows the org to be correct, as well as providing a response as to what was correct. A product label override is always required, since the location of the customer is not known and a suitable product label must be provided.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_label_override** | **str** | Override the default product label.  | 
**org_id** | **str** | Unique identifier | [optional] 
**components_fixed** | **[str]** | Components that were corrected in the fixup call  | [optional] 
**org** | [**Organisation**](Organisation.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


