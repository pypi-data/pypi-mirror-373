# ApplicationSummaryStatus

A high level summary about an application useful for displaying it in a catalogue. One of these exists per assignment of an application. For example, if an application has two instances and four assignments (two to each instance), there will be four of these objects for that application. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_id** | **str** | The ID of the application to which this organiastion is assigned. | 
**application_name** | **str** | The name of the application | 
**assigned_org_id** | **str** | The id of the organisation assigned to the application | 
**published** | **str** | Whether or not this Application is published, and if so, how. An application that has been published somewhere will have high level details about it visible, such as its name and description. The enum values mean the following:   - no: This application is not published. It will only be visibile to users with       permission to access the application, or to administrators.   - public: This application is published to the public catalogue. Any user who       can request access to the organisation will see high level details about this       application.  | 
**icon_url** | **str** | A url pointing to an icon representing this application.  | defaults to "https://storage.googleapis.com/agilicus/logo.svg"
**description** | **str** | A brief description of the application. | [optional] 
**category** | **str** | A category used to group similar applications together. | [optional] 
**default_role_name** | **str, none_type** | The name of the default role of the application. This will be granted to users by default when an admin grants access to this application in response to a request for access.  | [optional] 
**default_role_id** | **str, none_type** | The unique id the default role of the application. This will be granted to users by default when an admin grants access to this application in response to a request for access.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


