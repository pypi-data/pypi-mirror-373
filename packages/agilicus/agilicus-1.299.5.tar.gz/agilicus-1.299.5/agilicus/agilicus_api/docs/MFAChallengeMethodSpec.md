# MFAChallengeMethodSpec

Configuration for a specific multi-factor authentication challenge.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**priority** | **int** | The priority of this challenge method. Priority is how the user specifies which challenge method to be notified with if that method is supported.  A priority of 1 is the highest priority and indicates that the user prefers this challenge method. | 
**challenge_type** | **str** | The type of challenge to issue. This controls how the user is informed of the challenge, as well as how the challenge can be satisfied. The follow types are supported:   - sms:  a &#x60;sms&#x60; challenge informs the user via text message of the challenge. The challenge can     be answered via the link provided in the text message. The user can deny the challenge via this     mechanism as well.   - web_push: a &#x60;web_push&#x60; challenge informs the user of the challenge on every device they have   registered via the web push (rfc8030) mechanism. If the user accepts via the link provided in   the web push, the challenge will be satisfied. The user can deny the challenge via this   mechanism as well.   - totp: a time-based one-time password challenge allows the user to enter the code from their registered   - webauthn: a challenge issued for a specific device the user has possession of. Either a yubikey, or a phone that has a Trusted Platform Module.   device and application.   - one_time_use_action: a challenge whose acceptance or rejection takes an action on behalf of a user. Typically this is used   when wanting to respond to events through a messaging platform.   - code: a one time use challenge which may be redeemed through a code. This code is typically shared to the user who copies it from one machine   to another. This is a variation of web_push where, instead of sending the code via webpush, the caller runs their own protocol to communicate it.   The same answer mechanism (a link) is used. enum: [sms, web_push, totp, webauthn, one_time_use_action, code] example: web_push  | 
**endpoint** | **str** | The specific device to issue the challenge to. The meaning of this field may change depending on the challenge type specified. | 
**origin** | **str** | The origin the method was registered at. This is only used if the challenge type is WebAuthN | [optional] 
**nickname** | **str** | A descriptive name the user can set to differentiate their challenge methods. | [optional] 
**enabled** | **bool** | The state of the challenge method. A value of true indicates that the method is active. A value of false indicates that the method is disabled. When a method is disabled it will not be used as an authentication factor when the user logs in.  | [optional] 
**any string name** | **bool, date, datetime, dict, float, int, list, str, none_type** | any string name can be used but the value must be the correct type | [optional]

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


