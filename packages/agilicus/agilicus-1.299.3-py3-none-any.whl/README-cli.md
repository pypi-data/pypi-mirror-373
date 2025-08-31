# Agilicus CLI Command Reference

This document provides a comprehensive reference for all CLI commands available in the Agilicus CLI tool, organized by functional categories.

## Table of Contents

- [Users](#users)
- [Resources](#resources)
- [Identity](#identity)
- [Billing](#billing)
- [Operations](#operations)
- [Policy](#policy)
- [Miscellaneous](#miscellaneous)

---

## Users

Commands for managing users, groups, service accounts, permissions, SSH access, desktops, shares, and launchers.

### User Management

#### `list-users`
**Usage:** `agilicus list-users [OPTIONS]`

Lists users in the system with various filtering options.

**Arguments:**
- `--organisation` - Filter by organisation name
- `--org-id` - Filter by organisation ID
- `--email` - Filter by email address
- `--previous-email` - Filter by previous email
- `--limit` - Maximum number of results (default: None)
- `--status` - Filter by user status (multiple values allowed)
- `--search-direction` - Search direction (forwards/backwards)
- `--has-roles` - Filter users with roles (boolean)
- `--has-resource-roles` - Filter users with resource roles (boolean)
- `--prefix-email-search` - Email prefix search
- `--first-name` - Filter by first name
- `--last-name` - Filter by last name
- `--user-id` - Filter by user ID
- `--search-param` - Additional search parameters (multiple)
- `--allow-partial-match` - Allow partial matching
- `--type` - User type filter (multiple)
- `--upstream-idp-id` - Upstream IDP ID
- `--upstream-user-id` - Upstream user ID
- `--issuer` - Issuer filter
- `--has-application-permissions` - Filter by application permissions
- `--show-columns` - Specify columns to show
- `--reset-columns` - Reset column display
- `--has-resource-or-application-roles` - Filter by resource or application roles

#### `show-user`
**Usage:** `agilicus show-user EMAIL_OR_ID [OPTIONS]`

Shows detailed information about a specific user.

**Arguments:**
- `EMAIL_OR_ID` - User email address or ID
- `--org-id` - Organisation ID

#### `add-user`
**Usage:** `agilicus add-user FIRST_NAME LAST_NAME EMAIL ORG_ID [OPTIONS]`

Creates a new user in the system.

**Arguments:**
- `FIRST_NAME` - User's first name
- `LAST_NAME` - User's last name
- `EMAIL` - User's email address
- `ORG_ID` - Organisation ID
- `--external-id` - External identifier
- `--enabled` - Enable/disable user (boolean)
- `--status` - User status
- `--description` - User description

#### `update-user`
**Usage:** `agilicus update-user EMAIL_OR_ID [OPTIONS]`

Updates an existing user's information.

**Arguments:**
- `EMAIL_OR_ID` - User email address or ID
- `--email` - New email address
- `--org-id` - Organisation ID
- `--first-name` - New first name
- `--last-name` - New last name
- `--external-id` - External identifier
- `--auto-created` - Auto-created flag (boolean)
- `--enabled` - Enable/disable user (boolean)
- `--cascade` - Cascade changes (boolean)
- `--status` - User status
- `--description` - User description
- `--attribute` - User attributes (key-value pairs, multiple)
- `--remove-attribute` - Attributes to remove (multiple)
- `--disabled-at-time` - Disable timestamp

#### `delete-user`
**Usage:** `agilicus delete-user EMAIL [OPTIONS]`

Deletes a user from the system.

**Arguments:**
- `EMAIL` - User email address
- `--org-id` - Organisation ID

### User Roles and Permissions

#### `add-user-role`
**Usage:** `agilicus add-user-role EMAIL_OR_ID APPLICATION [OPTIONS]`

Adds roles to a user for a specific application.

**Arguments:**
- `EMAIL_OR_ID` - User email address or ID
- `APPLICATION` - Application name
- `--role` - Role names to add (multiple)
- `--org-id` - Organisation ID
- `--update` - Update existing roles

#### `list-user-roles`
**Usage:** `agilicus list-user-roles EMAIL [OPTIONS]`

Lists all roles assigned to a user.

**Arguments:**
- `EMAIL` - User email address
- `--org-id` - Organisation ID

#### `list-elevated-permissions`
**Usage:** `agilicus list-elevated-permissions [OPTIONS]`

Lists elevated permissions for users.

**Arguments:**
- `--user-id` - User ID (defaults to current user)
- `--limit` - Maximum number of results

#### `show-elevated-permissions`
**Usage:** `agilicus show-elevated-permissions USER_ID`

Shows elevated permissions for a specific user.

**Arguments:**
- `USER_ID` - User ID

#### `add-elevated-permissions`
**Usage:** `agilicus add-elevated-permissions USER_ID APPLICATION NAME`

Adds elevated permissions to a user.

**Arguments:**
- `USER_ID` - User ID
- `APPLICATION` - Application name
- `NAME` - Permission name

#### `delete-elevated-permissions`
**Usage:** `agilicus delete-elevated-permissions USER_ID APPLICATION NAME`

Removes elevated permissions from a user.

**Arguments:**
- `USER_ID` - User ID
- `APPLICATION` - Application name
- `NAME` - Permission name

#### `clear-elevated-permissions`
**Usage:** `agilicus clear-elevated-permissions USER_ID`

Clears all elevated permissions for a user.

**Arguments:**
- `USER_ID` - User ID

### Groups

#### `list-groups`
**Usage:** `agilicus list-groups [OPTIONS]`

Lists groups in the system.

**Arguments:**
- `--organisation` - Organisation name
- `--org-id` - Organisation ID
- `--type` - Group type (default: group)
- `--limit` - Maximum results (default: 500)
- `--previous-email` - Previous email filter
- `--prefix-email-search` - Email prefix search
- `--hide-members` - Hide group members (boolean)
- `--search-direction` - Search direction
- `--first-name` - First name filter
- `--last-name` - Last name filter
- `--search-param` - Search parameters (multiple)
- `--allow-partial-match` - Allow partial matching

#### `list-sysgroups`
**Usage:** `agilicus list-sysgroups [OPTIONS]`

Lists system groups.

**Arguments:**
- `--organisation` - Organisation name
- `--org-id` - Organisation ID
- `--hide-members` - Hide group members (boolean)

#### `add-group`
**Usage:** `agilicus add-group FIRST_NAME [OPTIONS]`

Creates a new group.

**Arguments:**
- `FIRST_NAME` - Group name
- `--org-id` - Organisation ID
- `--type` - Group type (default: group)
- `--cascade` - Cascade creation

#### `show-group`
**Usage:** `agilicus show-group GROUP_ID [OPTIONS]`

Shows detailed information about a group.

**Arguments:**
- `GROUP_ID` - Group ID
- `--org-id` - Organisation ID

#### `add-group-member`
**Usage:** `agilicus add-group-member GROUP_ID [OPTIONS]`

Adds members to a group.

**Arguments:**
- `GROUP_ID` - Group ID
- `--org-id` - Organisation ID
- `--member-org-id` - Member organisation ID
- `--member` - Member IDs (multiple)
- `--email` - Member emails (multiple)

#### `delete-group-member`
**Usage:** `agilicus delete-group-member GROUP_ID [OPTIONS]`

Removes members from a group.

**Arguments:**
- `GROUP_ID` - Group ID
- `--member` - Member IDs to remove (multiple)
- `--org-id` - Organisation ID

#### `delete-group`
**Usage:** `agilicus delete-group GROUP_ID`

Deletes a group.

**Arguments:**
- `GROUP_ID` - Group ID

### Service Accounts

#### `list-service-accounts`
**Usage:** `agilicus list-service-accounts [OPTIONS]`

Lists service accounts.

**Arguments:**
- `--org-id` - Organisation ID
- `--user-id` - User ID
- `--limit` - Maximum results (default: 500)

#### `add-service-account`
**Usage:** `agilicus add-service-account ORG_ID NAME [OPTIONS]`

Creates a new service account.

**Arguments:**
- `ORG_ID` - Organisation ID
- `NAME` - Service account name
- `--enabled/--disabled` - Enable/disable account
- `--allowed_sub_org` - Allowed sub-organisations (multiple)
- `--description` - Account description

#### `show-service-account`
**Usage:** `agilicus show-service-account SERVICE_ACCOUNT_ID [OPTIONS]`

Shows service account details.

**Arguments:**
- `SERVICE_ACCOUNT_ID` - Service account ID
- `--org-id` - Organisation ID

#### `delete-service-account`
**Usage:** `agilicus delete-service-account SERVICE_ACCOUNT_ID [OPTIONS]`

Deletes a service account.

**Arguments:**
- `SERVICE_ACCOUNT_ID` - Service account ID
- `--org-id` - Organisation ID

#### `update-service-account`
**Usage:** `agilicus update-service-account SERVICE_ACCOUNT_ID [OPTIONS]`

Updates a service account.

**Arguments:**
- `SERVICE_ACCOUNT_ID` - Service account ID
- `--name` - New name
- `--enabled/--disabled` - Enable/disable account
- `--allowed_sub_org` - Allowed sub-organisations (multiple)
- `--description` - Account description
- `--org-id` - Organisation ID

### User Access Information

#### `list-user-application-access-info`
**Usage:** `agilicus list-user-application-access-info [OPTIONS]`

Lists user's application access information.

**Arguments:**
- `--user` - User email or ID
- `--org-id` - Organisation ID
- `--resource-id` - Resource ID
- `--limit` - Maximum results (default: 500)

#### `list-user-fileshare-access-info`
**Usage:** `agilicus list-user-fileshare-access-info [OPTIONS]`

Lists user's file share access information.

**Arguments:**
- `--user` - User email or ID
- `--org-id` - Organisation ID
- `--resource-id` - Resource ID
- `--limit` - Maximum results (default: 500)

#### `list-user-desktop-access-info`
**Usage:** `agilicus list-user-desktop-access-info [OPTIONS]`

Lists user's desktop access information.

**Arguments:**
- `--user` - User email or ID
- `--org-id` - Organisation ID
- `--desktop-type` - Desktop type
- `--resource-id` - Resource ID
- `--limit` - Maximum results (default: 500)

#### `list-user-resource-access-info`
**Usage:** `agilicus list-user-resource-access-info [OPTIONS]`

Lists user's resource access information.

**Arguments:**
- `--user` - User email or ID
- `--org-id` - Organisation ID
- `--resource-id` - Resource ID
- `--include_all_resource_type` - Include all resource types (default: True)
- `--resource-type` - Resource type filter
- `--limit` - Maximum results (default: 500)

#### `list-user-ssh-access-info`
**Usage:** `agilicus list-user-ssh-access-info [OPTIONS]`

Lists user's SSH access information.

**Arguments:**
- `--user` - User email or ID
- `--org-id` - Organisation ID
- `--resource-id` - Resource ID
- `--limit` - Maximum results (default: 500)

#### `list-user-launcher-access-info`
**Usage:** `agilicus list-user-launcher-access-info [OPTIONS]`

Lists user's launcher access information.

**Arguments:**
- `--user` - User email or ID
- `--org-id` - Organisation ID
- `--resource-id` - Resource ID
- `--limit` - Maximum results (default: 500)

### User Requests

#### `list-user-requests`
**Usage:** `agilicus list-user-requests [OPTIONS]`

Lists user access requests.

**Arguments:**
- `--user-id` - User ID
- `--org-id` - Organisation ID
- `--request-type` - Request type
- `--request-state` - Request state
- `--limit` - Maximum results (default: 500)
- `--expired` - Filter expired requests (boolean)

#### `add-user-request`
**Usage:** `agilicus add-user-request USER_ID ORG_ID REQUESTED_RESOURCE REQUESTED_RESOURCE_TYPE [OPTIONS]`

Creates a new user access request.

**Arguments:**
- `USER_ID` - User ID
- `ORG_ID` - Organisation ID
- `REQUESTED_RESOURCE` - Requested resource
- `REQUESTED_RESOURCE_TYPE` - Resource type
- `--request-information` - Request information
- `--requested-sub-resource` - Sub-resource
- `--expiry-date` - Expiry date
- `--from-date` - From date
- `--to-date` - To date

#### `update-user-request`
**Usage:** `agilicus update-user-request USER_REQUEST_ID [OPTIONS]`

Updates a user access request.

**Arguments:**
- `USER_REQUEST_ID` - Request ID
- `--org-id` - Organisation ID
- `--user-id` - User ID
- `--requested-resource` - Requested resource
- `--requested-sub-resource` - Sub-resource
- `--requested-resource-type` - Resource type
- `--request-information` - Request information
- `--response-information` - Response information

#### `action-user-request`
**Usage:** `agilicus action-user-request USER_REQUEST_ID STATE [OPTIONS]`

Takes action on a user access request.

**Arguments:**
- `USER_REQUEST_ID` - Request ID
- `STATE` - Action state (approved/declined)
- `--org-id` - Organisation ID
- `--requested-resource` - Requested resource
- `--requested-resource-type` - Resource type
- `--request-information` - Request information

#### `bulk-action-user-request`
**Usage:** `agilicus bulk-action-user-request [OPTIONS]`

Takes bulk action on user requests.

**Arguments:**
- `--user-id` - User ID (required)
- `--org-id` - Organisation ID
- `--state` - Action state (approved/declined)
- `--user-status` - User status
- `--reset-user` - Reset user (boolean)

#### `show-user-request`
**Usage:** `agilicus show-user-request USER_REQUEST_ID [OPTIONS]`

Shows details of a user request.

**Arguments:**
- `USER_REQUEST_ID` - Request ID
- `--user-id` - User ID
- `--org-id` - Organisation ID

#### `delete-user-request`
**Usage:** `agilicus delete-user-request USER_REQUEST_ID [OPTIONS]`

Deletes a user request.

**Arguments:**
- `USER_REQUEST_ID` - Request ID
- `--user-id` - User ID
- `--org-id` - Organisation ID

#### `list-access-requests`
**Usage:** `agilicus list-access-requests [OPTIONS]`

Lists access requests.

**Arguments:**
- `--org-id` - Organisation ID
- `--user-id` - User ID
- `--request-type` - Request type
- `--request-state` - Request state
- `--limit` - Maximum results (default: 500)
- `--email` - Email filter
- `--search-direction` - Search direction

### User Metadata

#### `list-user-metadata`
**Usage:** `agilicus list-user-metadata [OPTIONS]`

Lists user metadata.

**Arguments:**
- `--user-id` - User ID
- `--org-id` - Organisation ID
- `--data-type` - Data type
- `--app-id` - Application ID
- `--recursive` - Recursive search (boolean)
- `--limit` - Maximum results (default: 500)

#### `add-user-metadata`
**Usage:** `agilicus add-user-metadata USER_ID ORG_ID DATA_TYPE DATA [OPTIONS]`

Adds metadata to a user.

**Arguments:**
- `USER_ID` - User ID
- `ORG_ID` - Organisation ID
- `DATA_TYPE` - Data type (mfa_enrollment_expiry, user_app_data, user_org_data, json)
- `DATA` - Metadata data
- `--app-id` - Application ID
- `--name` - Metadata name

#### `update-user-metadata`
**Usage:** `agilicus update-user-metadata USER_METADATA_ID [OPTIONS]`

Updates user metadata.

**Arguments:**
- `USER_METADATA_ID` - Metadata ID
- `--org-id` - Organisation ID
- `--user-id` - User ID
- `--data_type` - Data type
- `--data` - Metadata data
- `--app-id` - Application ID
- `--name` - Metadata name

#### `show-user-metadata`
**Usage:** `agilicus show-user-metadata USER_METADATA_ID [OPTIONS]`

Shows user metadata details.

**Arguments:**
- `USER_METADATA_ID` - Metadata ID
- `--user-id` - User ID
- `--org-id` - Organisation ID

#### `delete-user-metadata`
**Usage:** `agilicus delete-user-metadata USER_METADATA_ID [OPTIONS]`

Deletes user metadata.

**Arguments:**
- `USER_METADATA_ID` - Metadata ID
- `--user-id` - User ID
- `--org-id` - Organisation ID

#### `bulk-set-metadata`
**Usage:** `agilicus bulk-set-metadata ORG_ID DATA_TYPE DATA [OPTIONS]`

Sets metadata for multiple users.

**Arguments:**
- `ORG_ID` - Organisation ID
- `DATA_TYPE` - Data type
- `DATA` - Metadata data
- `--app-id` - Application ID
- `--name` - Metadata name

---

## Resources

Commands for managing applications, networks, resources, environments, labels, icons, and related configurations.

### Applications

#### `list-applications`
**Usage:** `agilicus list-applications [OPTIONS]`

Lists applications in the system.

**Arguments:**
- `--organisation` - Organisation name
- `--org-id` - Organisation ID
- `--resource-id` - Resource ID
- `--updated_since` - Updated since timestamp
- `--maintained/--no-maintained` - Filter by maintenance status
- `--owned/--no-owned` - Filter by ownership
- `--assigned/--no-assigned` - Filter by assignment
- `--include-migrated-environments/--exclude-migrated-environments` - Include migrated environments

#### `show-application`
**Usage:** `agilicus show-application APP [OPTIONS]`

Shows detailed information about an application.

**Arguments:**
- `APP` - Application name
- `--org-id` - Organisation ID
- `--include-migrated-environments` - Include migrated environments (default: True)

#### `add-application`
**Usage:** `agilicus add-application NAME ORG_ID CATEGORY [OPTIONS]`

Creates a new application.

**Arguments:**
- `NAME` - Application name
- `ORG_ID` - Organisation ID
- `CATEGORY` - Application category
- `--published` - Publication status (no/public)
- `--default-role-id` - Default role ID
- `--icon-url` - Icon URL
- `--location` - Location (hosted/external)
- `--service-account-required` - Require service account
- `--name-slug` - Name slug

#### `update-application`
**Usage:** `agilicus update-application APP [OPTIONS]`

Updates an existing application.

**Arguments:**
- `APP` - Application name
- `--image` - Application image
- `--port` - Application port
- `--org-id` - Organisation ID
- `--published` - Publication status (no/public)
- `--default-role-id` - Default role ID
- `--icon-url` - Icon URL
- `--location` - Location (hosted/external)
- `--service-account-id` - Service account ID
- `--service-account-required/--no-service-account-required` - Service account requirement
- `--name-slug` - Name slug
- `--admin-state` - Admin state (active/disabled)
- `--description` - Application description

#### `delete-application`
**Usage:** `agilicus delete-application APP [OPTIONS]`

Deletes an application.

**Arguments:**
- `APP` - Application name
- `--org-id` - Organisation ID

#### `assign-application`
**Usage:** `agilicus assign-application ENV_NAME APP_ID ORG_ID ASSIGNED_ORG_ID [OPTIONS]`

Assigns an application to an organisation.

**Arguments:**
- `ENV_NAME` - Environment name
- `APP_ID` - Application ID
- `ORG_ID` - Organisation ID
- `ASSIGNED_ORG_ID` - Assigned organisation ID
- `--admin-org-id` - Admin organisation ID

#### `unassign-application`
**Usage:** `agilicus unassign-application ENV_NAME APP_ID ORG_ID ASSIGNED_ORG_ID`

Unassigns an application from an organisation.

**Arguments:**
- `ENV_NAME` - Environment name
- `APP_ID` - Application ID
- `ORG_ID` - Organisation ID
- `ASSIGNED_ORG_ID` - Assigned organisation ID

### Application Services

#### `list-application-services`
**Usage:** `agilicus list-application-services [OPTIONS]`

Lists application services.

**Arguments:**
- `--org-id` - Organisation ID
- `--updated-since` - Updated since timestamp
- `--protocol-type` - Protocol type (ip/fileshare/ssh)
- `--protocol-type-list` - Protocol types (multiple)
- `--hostname` - Hostname filter
- `--port` - Port filter
- `--name` - Name filter
- `--hostname_or_service_name` - Hostname or service name
- `--external_hostname_or_service` - External hostname or service
- `--show-status` - Show status information

#### `add-application-service`
**Usage:** `agilicus add-application-service NAME HOSTNAME PORT [OPTIONS]`

Creates a new application service.

**Arguments:**
- `NAME` - Service name
- `HOSTNAME` - Service hostname
- `PORT` - Service port
- `--org-id` - Organisation ID
- `--ipv4-addresses` - IPv4 addresses
- `--name-resolution` - Name resolution
- `--protocol` - Protocol
- `--tls-enabled/--tls-disabled` - TLS configuration
- `--tls-verify/--tls-no-verify` - TLS verification
- `--connector-id` - Connector ID
- `--connector-instance-id` - Connector instance ID
- `--learning-mode` - Learning mode (boolean)
- `--learning-mode-expiry` - Learning mode expiry
- `--diagnostic-mode` - Diagnostic mode (boolean)

#### `update-application-service`
**Usage:** `agilicus update-application-service ID [OPTIONS]`

Updates an application service.

**Arguments:**
- `ID` - Service ID
- `--name` - Service name
- `--hostname` - Service hostname
- `--port` - Service port
- `--org-id` - Organisation ID
- `--ipv4-addresses` - IPv4 addresses
- `--name-resolution` - Name resolution
- `--service-type` - Service type (vpn/agent/internet/ipsec)
- `--protocol` - Protocol
- `--connector-id` - Connector ID
- `--connector-instance-id` - Connector instance ID
- `--tls-enabled/--tls-disabled` - TLS configuration
- `--tls-verify/--tls-no-verify` - TLS verification
- `--disable-http2` - Disable HTTP/2 (boolean)
- `--expose-as-hostname` - Expose as hostname (boolean)
- `--learning-mode` - Learning mode (boolean)
- `--learning-mode-expiry` - Learning mode expiry
- `--diagnostic-mode` - Diagnostic mode (boolean)
- `--port-range` - Port range (comma-separated)
- `--source-port-override` - Source port override
- `--source-address-override` - Source address override
- `--dynamic-source-port-override` - Dynamic source port override (boolean)

#### `show-application-service`
**Usage:** `agilicus show-application-service ID [OPTIONS]`

Shows application service details.

**Arguments:**
- `ID` - Service ID
- `--org-id` - Organisation ID

#### `delete-application-service`
**Usage:** `agilicus delete-application-service NAME [OPTIONS]`

Deletes an application service.

**Arguments:**
- `NAME` - Service name
- `--org-id` - Organisation ID

#### `create-application-service-token`
**Usage:** `agilicus create-application-service-token ID [OPTIONS]`

Creates a token for an application service.

**Arguments:**
- `ID` - Service ID
- `--org_id` - Organisation ID

### Application Service Assignments

#### `add-application-service-assignment`
**Usage:** `agilicus add-application-service-assignment APP_SERVICE_NAME APP ENVIRONMENT_NAME [OPTIONS]`

Assigns an application service to an environment.

**Arguments:**
- `APP_SERVICE_NAME` - Application service name
- `APP` - Application name
- `ENVIRONMENT_NAME` - Environment name
- `--org-id` - Organisation ID
- `--expose-type` - Exposure type (not_exposed/application/path_prefix/hostname)
- `--expose-as-hostname` - Expose as hostname
- `--connection-mapping` - Connection mapping

#### `update-application-service-assignment`
**Usage:** `agilicus update-application-service-assignment APP_SERVICE_NAME APP ENVIRONMENT_NAME [OPTIONS]`

Updates an application service assignment.

**Arguments:**
- `APP_SERVICE_NAME` - Application service name
- `APP` - Application name
- `ENVIRONMENT_NAME` - Environment name
- `--org-id` - Organisation ID
- `--expose-type` - Exposure type
- `--expose-as-hostname` - Expose as hostname
- `--expose-as-hostname-list-json` - Hostname list (JSON)
- `--connection-mapping` - Connection mapping

#### `delete-application-service-assignment`
**Usage:** `agilicus delete-application-service-assignment APP_SERVICE_NAME APP ENVIRONMENT_NAME [OPTIONS]`

Deletes an application service assignment.

**Arguments:**
- `APP_SERVICE_NAME` - Application service name
- `APP` - Application name
- `ENVIRONMENT_NAME` - Environment name
- `--org-id` - Organisation ID

### Environments

#### `list-environments`
**Usage:** `agilicus list-environments APPLICATION [OPTIONS]`

Lists environments for an application.

**Arguments:**
- `APPLICATION` - Application name
- `--organisation` - Organisation name
- `--org-id` - Organisation ID
- `--filter` - Filter fields

#### `show-environment`
**Usage:** `agilicus show-environment APPLICATION ENV_NAME [OPTIONS]`

Shows environment details.

**Arguments:**
- `APPLICATION` - Application name
- `ENV_NAME` - Environment name
- `--org-id` - Organisation ID

#### `update-environment`
**Usage:** `agilicus update-environment APP ENV_NAME [OPTIONS]`

Updates an environment configuration.

**Arguments:**
- `APP` - Application name
- `ENV_NAME` - Environment name
- `--org-id` - Organisation ID
- `--version-tag` - Version tag
- `--serverless-image` - Serverless image
- `--config-mount-path` - Config mount path
- `--config-as-mount` - Config as mount (JSON)
- `--config-as-env` - Config as environment (JSON)
- `--secrets-mount-path` - Secrets mount path
- `--secrets-as-mount` - Secrets as mount
- `--secrets-as-env` - Secrets as environment
- `--domain-aliases` - Domain aliases (multiple)
- `--clear-aliases` - Clear aliases
- `--name-slug` - Name slug
- `--proxy-location` - Proxy location (in_cloud/on_site)
- `--application-configs-data` - Application configs (JSON string)
- `--application-configs-file` - Application configs (JSON file)

#### `delete-environment`
**Usage:** `agilicus delete-environment APP ENV_NAME [OPTIONS]`

Deletes an environment.

**Arguments:**
- `APP` - Application name
- `ENV_NAME` - Environment name
- `--org-id` - Organisation ID

#### `set-env-runtime-status`
**Usage:** `agilicus set-env-runtime-status APP ENV_NAME [OPTIONS]`

Sets environment runtime status.

**Arguments:**
- `APP` - Application name
- `ENV_NAME` - Environment name
- `--org-id` - Organisation ID
- `--overall-status` - Overall status
- `--running-replicas` - Running replicas
- `--error-message` - Error message
- `--restarts` - Restarts (JSON)
- `--cpu` - CPU usage (JSON)
- `--memory` - Memory usage
- `--running-image` - Running image
- `--running-hash` - Running hash

#### `get-env-status`
**Usage:** `agilicus get-env-status APP ENV_NAME [OPTIONS]`

Gets environment status.

**Arguments:**
- `APP` - Application name
- `ENV_NAME` - Environment name
- `--org-id` - Organisation ID
- `--organisation` - Organisation name

### Application Configuration

#### `list-config`
**Usage:** `agilicus list-config APPLICATION ENV_NAME [OPTIONS]`

Lists application configuration.

**Arguments:**
- `APPLICATION` - Application name
- `ENV_NAME` - Environment name
- `--org-id` - Organisation ID

#### `add-config`
**Usage:** `agilicus add-config APPLICATION ENV_NAME [OPTIONS]`

Adds application configuration.

**Arguments:**
- `APPLICATION` - Application name
- `ENV_NAME` - Environment name
- `--org-id` - Organisation ID
- `--filename` - Configuration filename
- `--config_type` - Configuration type (required)
- `--mount-path` - Mount path (required)
- `--mount-src-path` - Mount source path
- `--username` - Username
- `--hostname` - Hostname
- `--password` - Password
- `--share` - Share name
- `--domain` - Domain
- `--file-store-uri` - File store URI

#### `update-config`
**Usage:** `agilicus update-config APPLICATION ENV_NAME ID [OPTIONS]`

Updates application configuration.

**Arguments:**
- `APPLICATION` - Application name
- `ENV_NAME` - Environment name
- `ID` - Configuration ID
- `--org-id` - Organisation ID
- `--config_type` - Configuration type
- `--mount-path` - Mount path
- `--mount-src-path` - Mount source path
- `--username` - Username
- `--password` - Password
- `--share` - Share name
- `--domain` - Domain
- `--file-store-uri` - File store URI

#### `delete-config`
**Usage:** `agilicus delete-config APPLICATION ENV_NAME ID [OPTIONS]`

Deletes application configuration.

**Arguments:**
- `APPLICATION` - Application name
- `ENV_NAME` - Environment name
- `ID` - Configuration ID
- `--org-id` - Organisation ID

### Environment Variables

#### `list-env-vars`
**Usage:** `agilicus list-env-vars APPLICATION ENV_NAME [OPTIONS]`

Lists environment variables.

**Arguments:**
- `APPLICATION` - Application name
- `ENV_NAME` - Environment name
- `--org-id` - Organisation ID
- `--secret` - Include secrets (default: True)

#### `add-env-var`
**
Usage:** `agilicus add-env-var APPLICATION ENV_NAME NAME VALUE [OPTIONS]`

Adds an environment variable.

**Arguments:**
- `APPLICATION` - Application name
- `ENV_NAME` - Environment name
- `NAME` - Variable name
- `VALUE` - Variable value
- `--org-id` - Organisation ID
- `--secret` - Mark as secret (boolean)

#### `update-env-var`
**Usage:** `agilicus update-env-var APPLICATION ENV_NAME NAME VALUE [OPTIONS]`

Updates an environment variable.

**Arguments:**
- `APPLICATION` - Application name
- `ENV_NAME` - Environment name
- `NAME` - Variable name
- `VALUE` - New variable value
- `--org-id` - Organisation ID
- `--secret` - Mark as secret (boolean)

#### `delete-env-var`
**Usage:** `agilicus delete-env-var APPLICATION ENV_NAME NAME [OPTIONS]`

Deletes an environment variable.

**Arguments:**
- `APPLICATION` - Application name
- `ENV_NAME` - Environment name
- `NAME` - Variable name
- `--org-id` - Organisation ID

### Networks

#### `list-networks`
**Usage:** `agilicus list-networks [OPTIONS]`

Lists networks in the system.

**Arguments:**
- `--org-id` - Organisation ID
- `--limit` - Maximum results (default: 500)

#### `add-network`
**Usage:** `agilicus add-network NAME CIDR [OPTIONS]`

Creates a new network.

**Arguments:**
- `NAME` - Network name
- `CIDR` - Network CIDR
- `--org-id` - Organisation ID
- `--description` - Network description

#### `show-network`
**Usage:** `agilicus show-network NETWORK_ID [OPTIONS]`

Shows network details.

**Arguments:**
- `NETWORK_ID` - Network ID
- `--org-id` - Organisation ID

#### `update-network`
**Usage:** `agilicus update-network NETWORK_ID [OPTIONS]`

Updates a network.

**Arguments:**
- `NETWORK_ID` - Network ID
- `--name` - Network name
- `--cidr` - Network CIDR
- `--org-id` - Organisation ID
- `--description` - Network description

#### `delete-network`
**Usage:** `agilicus delete-network NETWORK_ID [OPTIONS]`

Deletes a network.

**Arguments:**
- `NETWORK_ID` - Network ID
- `--org-id` - Organisation ID

### Resources

#### `list-resources`
**Usage:** `agilicus list-resources [OPTIONS]`

Lists resources in the system.

**Arguments:**
- `--org-id` - Organisation ID
- `--resource-type` - Resource type filter
- `--limit` - Maximum results (default: 500)

#### `show-resource`
**Usage:** `agilicus show-resource RESOURCE_ID [OPTIONS]`

Shows resource details.

**Arguments:**
- `RESOURCE_ID` - Resource ID
- `--org-id` - Organisation ID

### Labels

#### `list-labels`
**Usage:** `agilicus list-labels [OPTIONS]`

Lists labels in the system.

**Arguments:**
- `--org-id` - Organisation ID
- `--resource-type` - Resource type filter
- `--limit` - Maximum results (default: 500)

#### `add-label`
**Usage:** `agilicus add-label NAME [OPTIONS]`

Creates a new label.

**Arguments:**
- `NAME` - Label name
- `--org-id` - Organisation ID
- `--description` - Label description
- `--color` - Label color

#### `update-label`
**Usage:** `agilicus update-label LABEL_ID [OPTIONS]`

Updates a label.

**Arguments:**
- `LABEL_ID` - Label ID
- `--name` - Label name
- `--org-id` - Organisation ID
- `--description` - Label description
- `--color` - Label color

#### `delete-label`
**Usage:** `agilicus delete-label LABEL_ID [OPTIONS]`

Deletes a label.

**Arguments:**
- `LABEL_ID` - Label ID
- `--org-id` - Organisation ID

### Icons

#### `list-icons`
**Usage:** `agilicus list-icons [OPTIONS]`

Lists icons in the system.

**Arguments:**
- `--org-id` - Organisation ID
- `--limit` - Maximum results (default: 500)

#### `add-icon`
**Usage:** `agilicus add-icon NAME URL [OPTIONS]`

Creates a new icon.

**Arguments:**
- `NAME` - Icon name
- `URL` - Icon URL
- `--org-id` - Organisation ID
- `--description` - Icon description

#### `update-icon`
**Usage:** `agilicus update-icon ICON_ID [OPTIONS]`

Updates an icon.

**Arguments:**
- `ICON_ID` - Icon ID
- `--name` - Icon name
- `--url` - Icon URL
- `--org-id` - Organisation ID
- `--description` - Icon description

#### `delete-icon`
**Usage:** `agilicus delete-icon ICON_ID [OPTIONS]`

Deletes an icon.

**Arguments:**
- `ICON_ID` - Icon ID
- `--org-id` - Organisation ID

---

## Identity

Commands for managing identity providers, issuers, upstream providers, OIDC configurations, and authentication policies.

### Issuers

#### `list-issuers`
**Usage:** `agilicus list-issuers [OPTIONS]`

Lists identity issuers.

**Arguments:**
- `--org-id` - Organisation ID
- `--limit` - Maximum results (default: 500)

#### `add-issuer`
**Usage:** `agilicus add-issuer NAME ISSUER_URL [OPTIONS]`

Creates a new identity issuer.

**Arguments:**
- `NAME` - Issuer name
- `ISSUER_URL` - Issuer URL
- `--org-id` - Organisation ID
- `--description` - Issuer description
- `--enabled` - Enable issuer (boolean)

#### `show-issuer`
**Usage:** `agilicus show-issuer ISSUER_ID [OPTIONS]`

Shows issuer details.

**Arguments:**
- `ISSUER_ID` - Issuer ID
- `--org-id` - Organisation ID

#### `update-issuer`
**Usage:** `agilicus update-issuer ISSUER_ID [OPTIONS]`

Updates an issuer.

**Arguments:**
- `ISSUER_ID` - Issuer ID
- `--name` - Issuer name
- `--issuer-url` - Issuer URL
- `--org-id` - Organisation ID
- `--description` - Issuer description
- `--enabled` - Enable issuer (boolean)

#### `delete-issuer`
**Usage:** `agilicus delete-issuer ISSUER_ID [OPTIONS]`

Deletes an issuer.

**Arguments:**
- `ISSUER_ID` - Issuer ID
- `--org-id` - Organisation ID

### Upstream Providers

#### `list-upstream-providers`
**Usage:** `agilicus list-upstream-providers [OPTIONS]`

Lists upstream identity providers.

**Arguments:**
- `--org-id` - Organisation ID
- `--provider-type` - Provider type filter
- `--limit` - Maximum results (default: 500)

#### `add-upstream-provider`
**Usage:** `agilicus add-upstream-provider NAME PROVIDER_TYPE [OPTIONS]`

Creates a new upstream provider.

**Arguments:**
- `NAME` - Provider name
- `PROVIDER_TYPE` - Provider type (oidc/saml/ldap)
- `--org-id` - Organisation ID
- `--description` - Provider description
- `--enabled` - Enable provider (boolean)
- `--config` - Provider configuration (JSON)

#### `show-upstream-provider`
**Usage:** `agilicus show-upstream-provider PROVIDER_ID [OPTIONS]`

Shows upstream provider details.

**Arguments:**
- `PROVIDER_ID` - Provider ID
- `--org-id` - Organisation ID

#### `update-upstream-provider`
**Usage:** `agilicus update-upstream-provider PROVIDER_ID [OPTIONS]`

Updates an upstream provider.

**Arguments:**
- `PROVIDER_ID` - Provider ID
- `--name` - Provider name
- `--provider-type` - Provider type
- `--org-id` - Organisation ID
- `--description` - Provider description
- `--enabled` - Enable provider (boolean)
- `--config` - Provider configuration (JSON)

#### `delete-upstream-provider`
**Usage:** `agilicus delete-upstream-provider PROVIDER_ID [OPTIONS]`

Deletes an upstream provider.

**Arguments:**
- `PROVIDER_ID` - Provider ID
- `--org-id` - Organisation ID

### OIDC Configuration

#### `list-oidc-configs`
**Usage:** `agilicus list-oidc-configs [OPTIONS]`

Lists OIDC configurations.

**Arguments:**
- `--org-id` - Organisation ID
- `--limit` - Maximum results (default: 500)

#### `add-oidc-config`
**Usage:** `agilicus add-oidc-config NAME CLIENT_ID CLIENT_SECRET [OPTIONS]`

Creates a new OIDC configuration.

**Arguments:**
- `NAME` - Configuration name
- `CLIENT_ID` - OIDC client ID
- `CLIENT_SECRET` - OIDC client secret
- `--org-id` - Organisation ID
- `--issuer-url` - Issuer URL
- `--scopes` - OIDC scopes (multiple)
- `--enabled` - Enable configuration (boolean)

#### `show-oidc-config`
**Usage:** `agilicus show-oidc-config CONFIG_ID [OPTIONS]`

Shows OIDC configuration details.

**Arguments:**
- `CONFIG_ID` - Configuration ID
- `--org-id` - Organisation ID

#### `update-oidc-config`
**Usage:** `agilicus update-oidc-config CONFIG_ID [OPTIONS]`

Updates an OIDC configuration.

**Arguments:**
- `CONFIG_ID` - Configuration ID
- `--name` - Configuration name
- `--client-id` - OIDC client ID
- `--client-secret` - OIDC client secret
- `--org-id` - Organisation ID
- `--issuer-url` - Issuer URL
- `--scopes` - OIDC scopes (multiple)
- `--enabled` - Enable configuration (boolean)

#### `delete-oidc-config`
**Usage:** `agilicus delete-oidc-config CONFIG_ID [OPTIONS]`

Deletes an OIDC configuration.

**Arguments:**
- `CONFIG_ID` - Configuration ID
- `--org-id` - Organisation ID

### Authentication Policies

#### `list-auth-policies`
**Usage:** `agilicus list-auth-policies [OPTIONS]`

Lists authentication policies.

**Arguments:**
- `--org-id` - Organisation ID
- `--policy-type` - Policy type filter
- `--limit` - Maximum results (default: 500)

#### `add-auth-policy`
**Usage:** `agilicus add-auth-policy NAME POLICY_TYPE [OPTIONS]`

Creates a new authentication policy.

**Arguments:**
- `NAME` - Policy name
- `POLICY_TYPE` - Policy type
- `--org-id` - Organisation ID
- `--description` - Policy description
- `--enabled` - Enable policy (boolean)
- `--rules` - Policy rules (JSON)

#### `show-auth-policy`
**Usage:** `agilicus show-auth-policy POLICY_ID [OPTIONS]`

Shows authentication policy details.

**Arguments:**
- `POLICY_ID` - Policy ID
- `--org-id` - Organisation ID

#### `update-auth-policy`
**Usage:** `agilicus update-auth-policy POLICY_ID [OPTIONS]`

Updates an authentication policy.

**Arguments:**
- `POLICY_ID` - Policy ID
- `--name` - Policy name
- `--policy-type` - Policy type
- `--org-id` - Organisation ID
- `--description` - Policy description
- `--enabled` - Enable policy (boolean)
- `--rules` - Policy rules (JSON)

#### `delete-auth-policy`
**Usage:** `agilicus delete-auth-policy POLICY_ID [OPTIONS]`

Deletes an authentication policy.

**Arguments:**
- `POLICY_ID` - Policy ID
- `--org-id` - Organisation ID

---

## Billing

Commands for managing billing accounts, subscriptions, products, and payment information.

### Billing Accounts

#### `list-billing-accounts`
**Usage:** `agilicus list-billing-accounts [OPTIONS]`

Lists billing accounts.

**Arguments:**
- `--org-id` - Organisation ID
- `--account-status` - Account status filter
- `--limit` - Maximum results (default: 500)

#### `add-billing-account`
**Usage:** `agilicus add-billing-account NAME [OPTIONS]`

Creates a new billing account.

**Arguments:**
- `NAME` - Account name
- `--org-id` - Organisation ID
- `--description` - Account description
- `--billing-email` - Billing email address
- `--payment-method` - Payment method

#### `show-billing-account`
**Usage:** `agilicus show-billing-account ACCOUNT_ID [OPTIONS]`

Shows billing account details.

**Arguments:**
- `ACCOUNT_ID` - Account ID
- `--org-id` - Organisation ID

#### `update-billing-account`
**Usage:** `agilicus update-billing-account ACCOUNT_ID [OPTIONS]`

Updates a billing account.

**Arguments:**
- `ACCOUNT_ID` - Account ID
- `--name` - Account name
- `--org-id` - Organisation ID
- `--description` - Account description
- `--billing-email` - Billing email address
- `--payment-method` - Payment method

#### `delete-billing-account`
**Usage:** `agilicus delete-billing-account ACCOUNT_ID [OPTIONS]`

Deletes a billing account.

**Arguments:**
- `ACCOUNT_ID` - Account ID
- `--org-id` - Organisation ID

### Subscriptions

#### `list-subscriptions`
**Usage:** `agilicus list-subscriptions [OPTIONS]`

Lists subscriptions.

**Arguments:**
- `--org-id` - Organisation ID
- `--billing-account-id` - Billing account ID
- `--subscription-status` - Subscription status filter
- `--limit` - Maximum results (default: 500)

#### `add-subscription`
**Usage:** `agilicus add-subscription BILLING_ACCOUNT_ID PRODUCT_ID [OPTIONS]`

Creates a new subscription.

**Arguments:**
- `BILLING_ACCOUNT_ID` - Billing account ID
- `PRODUCT_ID` - Product ID
- `--org-id` - Organisation ID
- `--quantity` - Subscription quantity
- `--start-date` - Subscription start date

#### `show-subscription`
**Usage:** `agilicus show-subscription SUBSCRIPTION_ID [OPTIONS]`

Shows subscription details.

**Arguments:**
- `SUBSCRIPTION_ID` - Subscription ID
- `--org-id` - Organisation ID

#### `update-subscription`
**Usage:** `agilicus update-subscription SUBSCRIPTION_ID [OPTIONS]`

Updates a subscription.

**Arguments:**
- `SUBSCRIPTION_ID` - Subscription ID
- `--org-id` - Organisation ID
- `--quantity` - Subscription quantity
- `--product-id` - Product ID

#### `cancel-subscription`
**Usage:** `agilicus cancel-subscription SUBSCRIPTION_ID [OPTIONS]`

Cancels a subscription.

**Arguments:**
- `SUBSCRIPTION_ID` - Subscription ID
- `--org-id` - Organisation ID
- `--cancel-date` - Cancellation date

### Products

#### `list-products`
**Usage:** `agilicus list-products [OPTIONS]`

Lists available products.

**Arguments:**
- `--product-type` - Product type filter
- `--active-only` - Show only active products (boolean)
- `--limit` - Maximum results (default: 500)

#### `show-product`
**Usage:** `agilicus show-product PRODUCT_ID`

Shows product details.

**Arguments:**
- `PRODUCT_ID` - Product ID

---

## Operations

Commands for managing connectors, VPNs, organisations, features, clusters, audit destinations, points of presence, regions, and host bundles.

### Connectors

#### `list-connectors`
**Usage:** `agilicus list-connectors [OPTIONS]`

Lists connectors in the system.

**Arguments:**
- `--org-id` - Organisation ID
- `--connector-type` - Connector type filter
- `--status` - Connector status filter
- `--limit` - Maximum results (default: 500)

#### `add-connector`
**Usage:** `agilicus add-connector NAME CONNECTOR_TYPE [OPTIONS]`

Creates a new connector.

**Arguments:**
- `NAME` - Connector name
- `CONNECTOR_TYPE` - Connector type
- `--org-id` - Organisation ID
- `--description` - Connector description
- `--enabled` - Enable connector (boolean)
- `--config` - Connector configuration (JSON)

#### `show-connector`
**Usage:** `agilicus show-connector CONNECTOR_ID [OPTIONS]`

Shows connector details.

**Arguments:**
- `CONNECTOR_ID` - Connector ID
- `--org-id` - Organisation ID

#### `update-connector`
**Usage:** `agilicus update-connector CONNECTOR_ID [OPTIONS]`

Updates a connector.

**Arguments:**
- `CONNECTOR_ID` - Connector ID
- `--name` - Connector name
- `--connector-type` - Connector type
- `--org-id` - Organisation ID
- `--description` - Connector description
- `--enabled` - Enable connector (boolean)
- `--config` - Connector configuration (JSON)

#### `delete-connector`
**Usage:** `agilicus delete-connector CONNECTOR_ID [OPTIONS]`

Deletes a connector.

**Arguments:**
- `CONNECTOR_ID` - Connector ID
- `--org-id` - Organisation ID

#### `restart-connector`
**Usage:** `agilicus restart-connector CONNECTOR_ID [OPTIONS]`

Restarts a connector.

**Arguments:**
- `CONNECTOR_ID` - Connector ID
- `--org-id` - Organisation ID

### VPNs

#### `list-vpns`
**Usage:** `agilicus list-vpns [OPTIONS]`

Lists VPN configurations.

**Arguments:**
- `--org-id` - Organisation ID
- `--vpn-type` - VPN type filter
- `--status` - VPN status filter
- `--limit` - Maximum results (default: 500)

#### `add-vpn`
**Usage:** `agilicus add-vpn NAME VPN_TYPE [OPTIONS]`

Creates a new VPN configuration.

**Arguments:**
- `NAME` - VPN name
- `VPN_TYPE` - VPN type
- `--org-id` - Organisation ID
- `--description` - VPN description
- `--enabled` - Enable VPN (boolean)
- `--config` - VPN configuration (JSON)

#### `show-vpn`
**Usage:** `agilicus show-vpn VPN_ID [OPTIONS]`

Shows VPN configuration details.

**Arguments:**
- `VPN_ID` - VPN ID
- `--org-id` - Organisation ID

#### `update-vpn`
**Usage:** `agilicus update-vpn VPN_ID [OPTIONS]`

Updates a VPN configuration.

**Arguments:**
- `VPN_ID` - VPN ID
- `--name` - VPN name
- `--vpn-type` - VPN type
- `--org-id` - Organisation ID
- `--description` - VPN description
- `--enabled` - Enable VPN (boolean)
- `--config` - VPN configuration (JSON)

#### `delete-vpn`
**Usage:** `agilicus delete-vpn VPN_ID [OPTIONS]`

Deletes a VPN configuration.

**Arguments:**
- `VPN_ID` - VPN ID
- `--org-id` - Organisation ID

### Organisations

#### `list-organisations`
**Usage:** `agilicus list-organisations [OPTIONS]`

Lists organisations.

**Arguments:**
- `--parent-org-id` - Parent organisation ID
- `--org-type` - Organisation type filter
- `--status` - Organisation status filter
- `--limit` - Maximum results (default: 500)

#### `add-organisation`
**Usage:** `agilicus add-organisation NAME [OPTIONS]`

Creates a new organisation.

**Arguments:**
- `NAME` - Organisation name
- `--parent-org-id` - Parent organisation ID
- `--org-type` - Organisation type
- `--description` - Organisation description
- `--enabled` - Enable organisation (boolean)

#### `show-organisation`
**Usage:** `agilicus show-organisation ORG_ID`

Shows organisation details.

**Arguments:**
- `ORG_ID` - Organisation ID

#### `update-organisation`
**Usage:** `agilicus update-organisation ORG_ID [OPTIONS]`

Updates an organisation.

**Arguments:**
- `ORG_ID` - Organisation ID
- `--name` - Organisation name
- `--parent-org-id` - Parent organisation ID
- `--org-type` - Organisation type
- `--description` - Organisation description
- `--enabled` - Enable organisation (boolean)

#### `delete-organisation`
**Usage:** `agilicus delete-organisation ORG_ID`

Deletes an organisation.

**Arguments:**
- `ORG_ID` - Organisation ID

### Features

#### `list-features`
**Usage:** `agilicus list-features [OPTIONS]`

Lists system features.

**Arguments:**
- `--org-id` - Organisation ID
- `--feature-type` - Feature type filter
- `--enabled-only` - Show only enabled features (boolean)
- `--limit` - Maximum results (default: 500)

#### `enable-feature`
**Usage:** `agilicus enable-feature FEATURE_NAME [OPTIONS]`

Enables a system feature.

**Arguments:**
- `FEATURE_NAME` - Feature name
- `--org-id` - Organisation ID

#### `disable-feature`
**Usage:** `agilicus disable-feature FEATURE_NAME [OPTIONS]`

Disables a system feature.

**Arguments:**
- `FEATURE_NAME` - Feature name
- `--org-id` - Organisation ID

### Clusters

#### `list-clusters`
**Usage:** `agilicus list-clusters [OPTIONS]`

Lists clusters.

**Arguments:**
- `--cluster-type` - Cluster type filter
- `--status` - Cluster status filter
- `--region` - Region filter
- `--limit` - Maximum results (default: 500)

#### `show-cluster`
**Usage:** `agilicus show-cluster CLUSTER_ID`

Shows cluster details.

**Arguments:**
- `CLUSTER_ID` - Cluster ID

### Audit Destinations

#### `list-audit-destinations`
**Usage:** `agilicus list-audit-destinations [OPTIONS]`

Lists audit destinations.

**Arguments:**
- `--org-id` - Organisation ID
- `--destination-type` - Destination type filter
- `--enabled-only` - Show only enabled destinations (boolean)
- `--limit` - Maximum results (default: 500)

#### `add-audit-destination`
**Usage:** `agilicus add-audit-destination NAME DESTINATION_TYPE [OPTIONS]`

Creates a new audit destination.

**Arguments:**
- `NAME` - Destination name
- `DESTINATION_TYPE` - Destination type
- `--org-id` - Organisation ID
- `--description` - Destination description
- `--enabled` - Enable destination (boolean)
- `--config` - Destination configuration (JSON)

#### `show-audit-destination`
**Usage:** `agilicus show-audit-destination DESTINATION_ID [OPTIONS]`

Shows audit destination details.

**Arguments:**
- `DESTINATION_ID` - Destination ID
- `--org-id` - Organisation ID

#### `update-audit-destination`
**Usage:** `agilicus update-audit-destination DESTINATION_ID [OPTIONS]`

Updates an audit destination.

**Arguments:**
- `DESTINATION_ID` - Destination ID
- `--name` - Destination name
- `--destination-type` - Destination type
- `--org-id` - Organisation ID
- `--description` - Destination description
- `--enabled` - Enable destination (boolean)
- `--config` - Destination configuration (JSON)

#### `delete-audit-destination`
**Usage:** `agilicus delete-audit-destination DESTINATION_ID [OPTIONS]`

Deletes an audit destination.

**Arguments:**
- `DESTINATION_ID` - Destination ID
- `--org-id` - Organisation ID

### Points of Presence (PoP)

#### `list-pops`
**Usage:** `agilicus list-pops [OPTIONS]`

Lists points of presence.

**Arguments:**
- `--region` - Region filter
- `--status` - PoP status filter
- `--limit` - Maximum results (default: 500)

#### `show-pop`
**Usage:** `agilicus show-pop POP_ID`

Shows point of presence details.

**Arguments:**
- `POP_ID` - PoP ID

### Regions

#### `list-regions`
**Usage:** `agilicus list-regions [OPTIONS]`

Lists available regions.

**Arguments:**
- `--region-type` - Region type filter
- `--active-only` - Show only active regions (boolean)
- `--limit` - Maximum results (default: 500)

#### `show-region`
**Usage:** `agilicus show-region REGION_ID`

Shows region details.

**Arguments:**
- `REGION_ID` - Region ID

### Host Bundles

#### `list-host-bundles`
**Usage:** `agilicus list-host-bundles [OPTIONS]`

Lists host bundles.

**Arguments:**
- `--org-id` - Organisation ID
- `--bundle-type` - Bundle type filter
- `--status` - Bundle status filter
- `--limit` - Maximum results (default: 500)

#### `add-host-bundle`
**Usage:** `agilicus add-host-bundle NAME BUNDLE_TYPE [OPTIONS]`

Creates a new host bundle.

**Arguments:**
- `NAME` - Bundle name
- `BUNDLE_TYPE` - Bundle type
- `--org-id` - Organisation ID
- `--description` - Bundle description
- `--config` - Bundle configuration (JSON)

#### `show-host-bundle`
**Usage:** `agilicus show-host-bundle BUNDLE_ID [OPTIONS]`

Shows host bundle details.

**Arguments:**
- `BUNDLE_ID` - Bundle ID
- `--org-id` - Organisation ID

#### `update-host-bundle`
**Usage:** `agilicus update-host-bundle BUNDLE_ID [OPTIONS]`

Updates a host bundle.

**Arguments:**
- `BUNDLE_ID` - Bundle ID
- `--name` - Bundle name
- `--bundle-type` - Bundle type
- `--org-id` - Organisation ID
- `--description` - Bundle description
- `--config` - Bundle configuration (JSON)

#### `delete-host-bundle`
**Usage:** `agilicus delete-host-bundle BUNDLE_ID [OPTIONS]`

Deletes a host bundle.

**Arguments:**
- `BUNDLE_ID` - Bundle ID
- `--org-id` - Organisation ID

---

## Policy

Commands for managing policy rules and access control policies.

### Policy Rules

#### `list-policy-rules`
**Usage:** `agilicus list-policy-rules [OPTIONS]`

Lists policy rules.

**Arguments:**
- `--org-id` - Organisation ID
- `--rule-type` - Rule type filter
- `--resource-type` - Resource type filter
- `--enabled-only` - Show only enabled rules (boolean)
- `--limit` - Maximum results (default: 500)

#### `add-policy-rule`
**Usage:** `agilicus add-policy-rule NAME RULE_TYPE [OPTIONS]`

Creates a new policy rule.

**Arguments:**
- `NAME` - Rule name
- `RULE_TYPE` - Rule type
- `--org-id` - Organisation ID
- `--description` - Rule description
- `--enabled` - Enable rule (boolean)
- `--conditions` - Rule conditions (JSON)
- `--actions` - Rule actions (JSON)
- `--priority` - Rule priority

#### `show-policy-rule`
**Usage:** `agilicus show-policy-rule RULE_ID [OPTIONS]`

Shows policy rule details.

**Arguments:**
- `RULE_ID` - Rule ID
- `--org-id` - Organisation ID

#### `update-policy-rule`
**Usage:** `agilicus update-policy-rule RULE_ID [OPTIONS]`

Updates a policy rule.

**Arguments:**
- `RULE_ID` - Rule ID
- `--name` - Rule name
- `--rule-type` - Rule type
- `--org-id` - Organisation ID
- `--description` - Rule description
- `--enabled` - Enable rule (boolean)
- `--conditions` - Rule conditions (JSON)
- `--actions` - Rule actions (JSON)
- `--priority` - Rule priority

#### `delete-policy-rule`
**Usage:** `agilicus delete-policy-rule RULE_ID [OPTIONS]`

Deletes a policy rule.

**Arguments:**
- `RULE_ID` - Rule ID
- `--org-id` - Organisation ID

#### `enable-policy-rule`
**Usage:** `agilicus enable-policy-rule RULE_ID [OPTIONS]`

Enables a policy rule.

**Arguments:**
- `RULE_ID` - Rule ID
- `--org-id` - Organisation ID

#### `disable-policy-rule`
**Usage:** `agilicus disable-policy-rule RULE_ID [OPTIONS]`

Disables a policy rule.

**Arguments:**
- `RULE_ID` - Rule ID
- `--org-id` - Organisation ID

---

## Miscellaneous

Additional utility commands and system operations.

### System Information

#### `version`
**Usage:** `agilicus version`

Shows the CLI version information.

#### `config`
**Usage:** `agilicus config [OPTIONS]`

Shows or sets CLI configuration.

**Arguments:**
- `--show` - Show current configuration
- `--set` - Set configuration value (key=value format)
- `--unset` - Unset configuration key

#### `login`
**Usage:** `agilicus login [OPTIONS]`

Authenticates with the Agilicus platform.

**Arguments:**
- `--username` - Username for authentication
- `--password` - Password for authentication
- `--token` - Authentication token
- `--org-id` - Organisation ID

#### `logout`
**Usage:** `agilicus logout`

Logs out from the Agilicus platform.

#### `whoami`
**Usage:** `agilicus whoami`

Shows current user information.

### Data Export/Import

#### `export`
**Usage:** `agilicus export [OPTIONS]`

Exports data from the system.

**Arguments:**
- `--org-id` - Organisation ID
- `--resource-type` - Resource type to export
- `--format` - Export format (json/csv/yaml)
- `--output` - Output file path

#### `import`
**Usage:** `agilicus import FILE [OPTIONS]`

Imports data into the system.

**Arguments:**
- `FILE` - Import file path
- `--org-id` - Organisation ID
- `--format` - Import format (json/csv/yaml)
- `--dry-run` - Perform dry run without making changes

### Utilities

#### `validate`
**Usage:** `agilicus validate FILE [OPTIONS]`

Validates configuration files.

**Arguments:**
- `FILE` - Configuration file to validate
- `--schema` - Schema to validate against
- `--format` - File format (json/yaml)

#### `generate`
**Usage:** `agilicus generate TYPE [OPTIONS]`

Generates configuration templates.

**Arguments:**
- `TYPE` - Template type to generate
- `--output` - Output file path
- `--format` - Output format (json/yaml)

#### `health`
**Usage:** `agilicus health [OPTIONS]`

Checks system health status.

**Arguments:**
- `--org-id` - Organisation ID
- `--component` - Specific component to check
- `--verbose` - Verbose output

---

This comprehensive CLI reference covers all available commands in the Agilicus CLI tool, organized by functional categories for easy navigation and reference.
