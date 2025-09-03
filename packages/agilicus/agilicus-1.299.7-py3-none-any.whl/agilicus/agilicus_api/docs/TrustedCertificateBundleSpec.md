# TrustedCertificateBundleSpec

The Specification for a TrustedCertificateBundle.  Certificates are bundled based on the following:  - All labels that are 'included' will build the list  - All 'excluded' certificates will then be removed from the list 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**TrustedCertificateBundleName**](TrustedCertificateBundleName.md) |  | 
**org_id** | **str** | Unique identifier | 
**labels** | [**[TrustedCertificateBundleLabel]**](TrustedCertificateBundleLabel.md) | list of labels associated with this bundle | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


