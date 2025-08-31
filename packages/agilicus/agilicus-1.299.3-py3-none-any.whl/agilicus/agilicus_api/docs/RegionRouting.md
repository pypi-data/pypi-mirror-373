# RegionRouting

Describes how a Region may be accessed over the Internet. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**domains** | [**[Domain]**](Domain.md) | The domains that address this Region. Use these when configuring external systems such as a DNS CNAME or a firewall.  | 
**public** | **bool** | If true, this region is public and is visible to external systems. | [optional] 
**requests_enabled** | **bool** | If true, allow this Region to serve RoutingRequests. | [optional] 
**org_domains** | [**[Domain]**](Domain.md) | Organisation subdomains supported by this region | [optional] 
**restrict_by_user_id** | **bool** | If true, routing is restricted by user_id (see permitted_user_ids) | [optional] 
**permitted_user_ids** | **[str]** | A list of user_ids that are permitted for using this region on a routing request.  | [optional] 
**ces** | **str** | A Common Expression Library (CES) used to evaluate if a routing request should utilize this Region  The following objects are available to the ces program:      geoip:       iso_code:       city:       country:       currency:     token_info:       email:       sub:       org:  Example ces that evaluates to true if subscriber ip address is found in USA:      geoip.iso_code &#x3D;&#x3D; &#39;US&#39;  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


