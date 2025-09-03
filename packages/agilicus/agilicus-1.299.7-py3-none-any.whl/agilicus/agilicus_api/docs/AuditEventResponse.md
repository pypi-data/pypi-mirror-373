# AuditEventResponse

How the audit event was processed. This describes whether it was succesfull, and if not, what should be done (if anything) to rectify the situation. Optionally, extra information regarding any failures may be provided in the `status_message`. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**unique_id** | **str** | A unique ID that can be used to determine whether the event has been processed multiple times. This should never happen, but it can&#39;t hurt to be safe.  | 
**status** | **bool, date, datetime, dict, float, int, list, str, none_type** | How the event was processed. The possible values mean:    - success: The event was succesfully processed. It can be discarded.   - duplicate: the event was a duplicate. It should be discarded.   - invalid: the event was invlaid. It should be discarded.   - unprocessed: the event could not be processed for some reason. It should be retried.   - too_busy: the handler was too busy. Try this event again later. Something else in the response should hint at when would     be a good time.  An unknown status should be treated as invalid so that events do not queue up waiting to be processed. It is unlikely that the caller will know how to handle an unknown status so that it can rectify the problem.  | 
**status_message** | **bool, date, datetime, dict, float, int, list, str, none_type** | An optional message describing what happened with the event. This can be useful for diagnostics.  | [optional] 
**event** | **{str: (bool, date, datetime, dict, float, int, list, str, none_type)}** | The primary contents of the audit event. Optional for an audit response. Returning this can help with diagnostics, but it is not necessary.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


