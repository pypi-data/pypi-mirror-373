# FeatureTag

A FeatureTag is a simple attribute of the system which can be used to determine whether it is appropriate for a given usecase. For example, typically a user would filter or restrict regions based on a list of tags.  Each tag represents an orthogonal piece of information whose meaning if obvious from its value. When configuring the system, a customer may choose to provide a policy that controls into which regions they may deploy their assets. Such a policy may list say something like:    - Germany or France    - not high-cost In plain terms, that would say: \"We can deploy assets in non-high-cost regions located either in germany or france\".  The most basic use for a FeatureTag is a list of intedependent features that describe what an Organistion is allowed to do:   e.g. \"Can use shares\", or \"Can deploy in North American clusters\"  Features are referred to by name. The name is immutable. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**spec** | [**FeatureTagSpec**](FeatureTagSpec.md) |  | 
**metadata** | [**CommonMetadata**](CommonMetadata.md) |  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


