# ConnectorDiagnosticStats

Diagnostic statistics about the Connector and the system on which is is running. The list of statistics may change based on the version of the connector, the system on which it runs, or other external factors. Do not rely on any given statistic being present. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**generic_int_metrics** | [**[GenericIntMetric]**](GenericIntMetric.md) | The list of generic int metrics from the Connector. | 
**generic_float_metrics** | [**[GenericFloatMetric]**](GenericFloatMetric.md) | The list of generic float metrics from the Connector. | 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


