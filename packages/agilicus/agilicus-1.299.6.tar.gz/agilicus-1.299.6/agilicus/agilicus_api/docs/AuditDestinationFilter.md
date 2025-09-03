# AuditDestinationFilter

A filter describing which sort of events should be sent to a destination. If both value and or_list are set, the filter will match if either match. If neither are set, the filter trivially passes. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filter_type** | **str** | The property of the event to filter on. The property can be related to the event itself, or something about the source of the event. Possible values include:   - &#x60;subsystem&#x60;: The subsystem emitting the event. E.g. access. This typically decides the structure of the logs emitted.  - &#x60;phase&#x60;: The phase within the subsystem emitting the event. Not all subsystems have more than one phase.  - &#x60;audit_agent_type&#x60;: The type of the agent emitting the event. E.g. connector  - &#x60;audit_agent_id&#x60;: The identifier of the agent emitting the event. E.g. for a connector, this is the GUID of the connector.  - &#x60;hostname&#x60;: The hostname of the system on which the agent resides.  | 
**value** | **str** | The value to filter on. The possible values depend on the &#x60;filter_type&#x60;:  - &#x60;subsystem&#x60;: One of:     - &#x60;access&#x60;: Access events     - &#x60;authorization&#x60;: Authorization events - &#x60;phase&#x60;: This is reserved for future use. It currently has no meaning. - &#x60;audit_agent_type&#x60;: One of:   - &#x60;connector&#x60;: Any connector.   - &#x60;agent_connector&#x60;: An on-site agent connector. - &#x60;audit_agent_id&#x60;: A unique identifier for an audit agent. - &#x60;hostname&#x60;: A hostname.  | [optional] 
**or_list** | **[str]** | A list of values this filter can match. If it matches any of them, it passes.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


