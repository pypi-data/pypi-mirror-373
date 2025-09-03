# agilicus_api.FilesApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_file**](FilesApi.md#add_file) | **POST** /v1/files | upload a file
[**create_file_association**](FilesApi.md#create_file_association) | **POST** /v1/file_associations | associate a file with an object
[**create_file_association_clear_task**](FilesApi.md#create_file_association_clear_task) | **POST** /v1/file_association_clear | Cleans up file associations
[**create_file_template**](FilesApi.md#create_file_template) | **POST** /v1/file_templates | Add a file template
[**create_public_file_org_link**](FilesApi.md#create_public_file_org_link) | **POST** /v1/public_file_org_links | link public files based on org
[**delete_file**](FilesApi.md#delete_file) | **DELETE** /v1/files/{file_id} | Delete a File
[**delete_file_association**](FilesApi.md#delete_file_association) | **DELETE** /v1/file_associations/{file_association_id} | Remove an association from a file
[**delete_file_template**](FilesApi.md#delete_file_template) | **DELETE** /v1/file_templates/{file_template_id} | Delete a file template
[**delete_public_file_org_link**](FilesApi.md#delete_public_file_org_link) | **DELETE** /v1/public_file_org_links/{public_file_org_link_id} | Remove a link from an org
[**get_download**](FilesApi.md#get_download) | **GET** /v1/files_download/{file_id} | Download File
[**get_download_public**](FilesApi.md#get_download_public) | **GET** /v1/files_public | Download public file
[**get_file**](FilesApi.md#get_file) | **GET** /v1/files/{file_id} | Get File metadata
[**get_file_association**](FilesApi.md#get_file_association) | **GET** /v1/file_associations/{file_association_id} | Get a file association
[**get_file_template**](FilesApi.md#get_file_template) | **GET** /v1/file_templates/{file_template_id} | Get a file template
[**get_public_file_org_link**](FilesApi.md#get_public_file_org_link) | **GET** /v1/public_file_org_links/{public_file_org_link_id} | Get a public file org link
[**list_file_associations**](FilesApi.md#list_file_associations) | **GET** /v1/file_associations | Query File Associations
[**list_file_templates**](FilesApi.md#list_file_templates) | **GET** /v1/file_templates | List all file templates
[**list_files**](FilesApi.md#list_files) | **GET** /v1/files | Query Files
[**list_public_file_org_links**](FilesApi.md#list_public_file_org_links) | **GET** /v1/public_file_org_links | Query Public File Org Links
[**render_file_template**](FilesApi.md#render_file_template) | **POST** /v1/file_templates/{file_template_id}/render | Render a file template
[**replace_file**](FilesApi.md#replace_file) | **PUT** /v1/files/{file_id} | Update a file
[**replace_file_template**](FilesApi.md#replace_file_template) | **PUT** /v1/file_templates/{file_template_id} | update a file template
[**replace_public_file_org_link**](FilesApi.md#replace_public_file_org_link) | **PUT** /v1/public_file_org_links/{public_file_org_link_id} | Replace a public file org link
[**reupload_file**](FilesApi.md#reupload_file) | **PUT** /v1/files/{file_id}/upload | Upload a new version of a file


# **add_file**
> FileSummary add_file(name, file_zip)

upload a file

Upload a file

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.file_name import FileName
from agilicus_api.model.file_visibility import FileVisibility
from agilicus_api.model.file_summary import FileSummary
from agilicus_api.model.storage_region import StorageRegion
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    name = FileName("Alice") # FileName | 
    file_zip = open('/path/to/file', 'rb') # file_type | The contents of the file in binary format
    org_id = "123" # str | Unique identifier (optional)
    tag = "theme" # str | A file tag (optional)
    label = "label_example" # str | A file label (optional)
    region = StorageRegion("ca") # StorageRegion |  (optional)
    visibility = FileVisibility("private") # FileVisibility |  (optional)
    md5_hash = "md5_hash_example" # str | MD5 Hash of file in base64 (optional)

    # example passing only required values which don't have defaults set
    try:
        # upload a file
        api_response = api_instance.add_file(name, file_zip)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->add_file: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # upload a file
        api_response = api_instance.add_file(name, file_zip, org_id=org_id, tag=tag, label=label, region=region, visibility=visibility, md5_hash=md5_hash)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->add_file: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **FileName**|  |
 **file_zip** | **file_type**| The contents of the file in binary format |
 **org_id** | **str**| Unique identifier | [optional]
 **tag** | **str**| A file tag | [optional]
 **label** | **str**| A file label | [optional]
 **region** | [**StorageRegion**](StorageRegion.md)|  | [optional]
 **visibility** | [**FileVisibility**](FileVisibility.md)|  | [optional]
 **md5_hash** | **str**| MD5 Hash of file in base64 | [optional]

### Return type

[**FileSummary**](FileSummary.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully uploaded file |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_file_association**
> FileAssociation create_file_association(file_association)

associate a file with an object

associate a file with an objet

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.file_association import FileAssociation
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_association = FileAssociation(
        metadata=MetadataWithId(),
        spec=FileAssociationSpec(
            file_id="123",
            object_id="123",
            org_id="123",
        ),
        status=FileAssociationStatus(
            file_status=ObjectOperStatus("active"),
        ),
    ) # FileAssociation | The file association

    # example passing only required values which don't have defaults set
    try:
        # associate a file with an object
        api_response = api_instance.create_file_association(file_association)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->create_file_association: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_association** | [**FileAssociation**](FileAssociation.md)| The file association |

### Return type

[**FileAssociation**](FileAssociation.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created association |  -  |
**400** | The association was invalid. This could be because it was improperly formatted, or because the file had already been deleted/marked for deletion.  |  -  |
**409** | Association for this file and object already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_file_association_clear_task**
> ClearFileAssociationResponse create_file_association_clear_task(clear_file_association_request)

Cleans up file associations

Cleans up file associations, potentially marking files for garbage collection

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.clear_file_association_request import ClearFileAssociationRequest
from agilicus_api.model.clear_file_association_response import ClearFileAssociationResponse
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    clear_file_association_request = ClearFileAssociationRequest(
        object_id="123",
        org_id="123",
    ) # ClearFileAssociationRequest | The description of the cleanup task

    # example passing only required values which don't have defaults set
    try:
        # Cleans up file associations
        api_response = api_instance.create_file_association_clear_task(clear_file_association_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->create_file_association_clear_task: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **clear_file_association_request** | [**ClearFileAssociationRequest**](ClearFileAssociationRequest.md)| The description of the cleanup task |

### Return type

[**ClearFileAssociationResponse**](ClearFileAssociationResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully cleared associations. The response contains information about what was modified.  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_file_template**
> FileTemplate create_file_template(file_template)

Add a file template

Adds a new file template. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.file_template import FileTemplate
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_template = FileTemplate(
        metadata=MetadataWithId(),
        spec=FileTemplateSpec(
            template_parameters=[
                FileTemplateParameter(
                    name=FileTemplateParameterName("api_key"),
                    input_hint="agilicus.api_key.",
                ),
            ],
            template_content_type="application/zip",
            default_arguments=[
                FileTemplateArgument(
                    name=FileTemplateParameterName("api_key"),
                    value=None,
                ),
            ],
            purpose="project-file",
            template_file="123",
            org_id="123",
            descriptive_text="Project File",
            associated_objects=[
                FileTemplateAssociation(
                    object_id="123",
                    object_type=ObjectType("desktop"),
                    descriptive_text="descriptive_text_example",
                ),
            ],
            rendered_file_name="my-config.txt",
            delimiter="%",
        ),
    ) # FileTemplate | 

    # example passing only required values which don't have defaults set
    try:
        # Add a file template
        api_response = api_instance.create_file_template(file_template)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->create_file_template: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_template** | [**FileTemplate**](FileTemplate.md)|  |

### Return type

[**FileTemplate**](FileTemplate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New file template created. |  -  |
**400** | The request is invalid |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_public_file_org_link**
> PublicFileOrgLink create_public_file_org_link(public_file_org_link)

link public files based on org

links public files based on organisation and tag

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.public_file_org_link import PublicFileOrgLink
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    public_file_org_link = PublicFileOrgLink(
        metadata=MetadataWithId(),
        spec=PublicFileOrgLinkSpec(
            file_tag="theme",
            link_org_id=None,
            target_org_id=None,
        ),
    ) # PublicFileOrgLink | The link to create

    # example passing only required values which don't have defaults set
    try:
        # link public files based on org
        api_response = api_instance.create_public_file_org_link(public_file_org_link)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->create_public_file_org_link: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **public_file_org_link** | [**PublicFileOrgLink**](PublicFileOrgLink.md)| The link to create |

### Return type

[**PublicFileOrgLink**](PublicFileOrgLink.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successfully created link |  -  |
**400** | The link was invalid. This could be because it was improperly formatted.  |  -  |
**409** | A link for this org_id and file_tag already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_file**
> delete_file(file_id)

Delete a File

Delete a File

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_id = "1234" # str | file_id path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a File
        api_instance.delete_file(file_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->delete_file: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a File
        api_instance.delete_file(file_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->delete_file: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_id** | **str**| file_id path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | File was deleted |  -  |
**404** | File does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_file_association**
> delete_file_association(file_association_id)

Remove an association from a file

Remove an association from a file

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_association_id = "1234" # str | file association id in path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Remove an association from a file
        api_instance.delete_file_association(file_association_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->delete_file_association: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Remove an association from a file
        api_instance.delete_file_association(file_association_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->delete_file_association: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_association_id** | **str**| file association id in path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Association was deleted |  -  |
**404** | Association does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_file_template**
> delete_file_template(file_template_id)

Delete a file template

Delete a file template

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_template_id = "1234" # str | file_template_id in path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Delete a file template
        api_instance.delete_file_template(file_template_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->delete_file_template: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Delete a file template
        api_instance.delete_file_template(file_template_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->delete_file_template: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_template_id** | **str**| file_template_id in path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | FileTemplate was deleted |  -  |
**404** | FileTemplate does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_public_file_org_link**
> delete_public_file_org_link(public_file_org_link_id)

Remove a link from an org

Remove a link from an org. Note that link_org_id and org_id are alises for one another in this query. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    public_file_org_link_id = "1234" # str | public file org link id in path
    link_org_id = "1234" # str | Search for the Organisation that is linked to another (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Remove a link from an org
        api_instance.delete_public_file_org_link(public_file_org_link_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->delete_public_file_org_link: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Remove a link from an org
        api_instance.delete_public_file_org_link(public_file_org_link_id, link_org_id=link_org_id, org_id=org_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->delete_public_file_org_link: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **public_file_org_link_id** | **str**| public file org link id in path |
 **link_org_id** | **str**| Search for the Organisation that is linked to another | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

void (empty response body)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Link was deleted |  -  |
**404** | Link does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_download**
> file_type get_download(file_id)

Download File

Download File

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_id = "1234" # str | file_id path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Download File
        api_response = api_instance.get_download(file_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_download: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Download File
        api_response = api_instance.get_download(file_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_download: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_id** | **str**| file_id path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

**file_type**

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Downloaded |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_download_public**
> file_type get_download_public()

Download public file

Download public file

### Example

```python
import time
import agilicus_api
from agilicus_api.api import files_api
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)


# Enter a context with an instance of the API client
with agilicus_api.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    subdomain = "agilicus.cloud" # str | query based on organisation subdomain  (optional)
    label = "label-1" # str | Filters based on whether or not the items in the collection have the given label.  (optional)
    tag = "theme" # str | Search files based on tag (optional)
    file_in_zip = "favicon-32x32.png" # str | query based on file name inside a zip file  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Download public file
        api_response = api_instance.get_download_public(subdomain=subdomain, label=label, tag=tag, file_in_zip=file_in_zip)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_download_public: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **subdomain** | **str**| query based on organisation subdomain  | [optional]
 **label** | **str**| Filters based on whether or not the items in the collection have the given label.  | [optional]
 **tag** | **str**| Search files based on tag | [optional]
 **file_in_zip** | **str**| query based on file name inside a zip file  | [optional]

### Return type

**file_type**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/octet-stream, application/gzip


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Downloaded |  -  |
**403** | Query not allowed |  -  |
**404** | File does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_file**
> FileSummary get_file(file_id)

Get File metadata

Get File metadata

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.file_summary import FileSummary
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_id = "1234" # str | file_id path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get File metadata
        api_response = api_instance.get_file(file_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_file: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get File metadata
        api_response = api_instance.get_file(file_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_file: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_id** | **str**| file_id path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**FileSummary**](FileSummary.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return File by id |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_file_association**
> FileAssociation get_file_association(file_association_id)

Get a file association

Get a file association

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.file_association import FileAssociation
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_association_id = "1234" # str | file association id in path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a file association
        api_response = api_instance.get_file_association(file_association_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_file_association: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a file association
        api_response = api_instance.get_file_association(file_association_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_file_association: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_association_id** | **str**| file association id in path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**FileAssociation**](FileAssociation.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Association found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_file_template**
> FileTemplate get_file_template(file_template_id)

Get a file template

Get a file template

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.file_template import FileTemplate
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_template_id = "1234" # str | file_template_id in path
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a file template
        api_response = api_instance.get_file_template(file_template_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_file_template: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a file template
        api_response = api_instance.get_file_template(file_template_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_file_template: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_template_id** | **str**| file_template_id in path |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**FileTemplate**](FileTemplate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return a FileTemplate |  -  |
**404** | FileTemplate does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_public_file_org_link**
> PublicFileOrgLink get_public_file_org_link(public_file_org_link_id)

Get a public file org link

Get a public file org link. Note that link_org_id and org_id are alises for one another in this query. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.public_file_org_link import PublicFileOrgLink
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    public_file_org_link_id = "1234" # str | public file org link id in path
    link_org_id = "1234" # str | Search for the Organisation that is linked to another (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Get a public file org link
        api_response = api_instance.get_public_file_org_link(public_file_org_link_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_public_file_org_link: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get a public file org link
        api_response = api_instance.get_public_file_org_link(public_file_org_link_id, link_org_id=link_org_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->get_public_file_org_link: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **public_file_org_link_id** | **str**| public file org link id in path |
 **link_org_id** | **str**| Search for the Organisation that is linked to another | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**PublicFileOrgLink**](PublicFileOrgLink.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | link found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_file_associations**
> ListFileAssociationsResponse list_file_associations()

Query File Associations

Query File Associations

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.list_file_associations_response import ListFileAssociationsResponse
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    file_id = "1234" # str | search by file id (optional)
    object_id = "1234" # str | search by object id (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query File Associations
        api_response = api_instance.list_file_associations(limit=limit, org_id=org_id, file_id=file_id, object_id=object_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->list_file_associations: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **file_id** | **str**| search by file id | [optional]
 **object_id** | **str**| search by object id | [optional]

### Return type

[**ListFileAssociationsResponse**](ListFileAssociationsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return matching file associations |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_file_templates**
> ListFileTemplatesResponse list_file_templates()

List all file templates

List all file templates matching the provided query parameters. Perform keyset pagination by setting the page_at_id parameter to the id for the next page to fetch. Set it to `\"\"` to start from the beginning. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.list_file_templates_response import ListFileTemplatesResponse
from agilicus_api.model.object_type import ObjectType
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    purpose = "project-file" # str | The purpose of an item (optional)
    object_types = [
        ObjectType("["abA12"]"),
    ] # [ObjectType] | A list of object types. Returns all items which match at least one of the types.  (optional)
    object_ids = ["aba23"] # [str] | A list of object IDs. Returns all items which match at least one of the .  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List all file templates
        api_response = api_instance.list_file_templates(limit=limit, page_at_id=page_at_id, org_id=org_id, purpose=purpose, object_types=object_types, object_ids=object_ids)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->list_file_templates: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **purpose** | **str**| The purpose of an item | [optional]
 **object_types** | [**[ObjectType]**](ObjectType.md)| A list of object types. Returns all items which match at least one of the types.  | [optional]
 **object_ids** | **[str]**| A list of object IDs. Returns all items which match at least one of the .  | [optional]

### Return type

[**ListFileTemplatesResponse**](ListFileTemplatesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Query succeeded |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_files**
> ListFilesResponse list_files()

Query Files

Query Files

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.list_files_response import ListFilesResponse
from agilicus_api.model.object_oper_status import ObjectOperStatus
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    user_id = "1234" # str | Query based on user id (optional)
    tag = "theme" # str | Search files based on tag (optional)
    file_association_id = "1234" # str | search by file association's id (optional)
    object_oper_status = ObjectOperStatus("pending_delete") # ObjectOperStatus | search by object oper status (optional)
    has_been_associated = True # bool | Only return object that have ever been associated (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query Files
        api_response = api_instance.list_files(limit=limit, org_id=org_id, user_id=user_id, tag=tag, file_association_id=file_association_id, object_oper_status=object_oper_status, has_been_associated=has_been_associated)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->list_files: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **user_id** | **str**| Query based on user id | [optional]
 **tag** | **str**| Search files based on tag | [optional]
 **file_association_id** | **str**| search by file association&#39;s id | [optional]
 **object_oper_status** | **ObjectOperStatus**| search by object oper status | [optional]
 **has_been_associated** | **bool**| Only return object that have ever been associated | [optional]

### Return type

[**ListFilesResponse**](ListFilesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return files list |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_public_file_org_links**
> ListPublicFileOrgLinksResponse list_public_file_org_links()

Query Public File Org Links

Query Public File Org Links. Note that link_org_id and org_id are alises for one another in this query. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.list_public_file_org_links_response import ListPublicFileOrgLinksResponse
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    link_org_id = "1234" # str | Search for the Organisation that is linked to another (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)
    tag = "theme" # str | Search files based on tag (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Query Public File Org Links
        api_response = api_instance.list_public_file_org_links(limit=limit, link_org_id=link_org_id, org_id=org_id, tag=tag, page_at_id=page_at_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->list_public_file_org_links: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **link_org_id** | **str**| Search for the Organisation that is linked to another | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **tag** | **str**| Search files based on tag | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]

### Return type

[**ListPublicFileOrgLinksResponse**](ListPublicFileOrgLinksResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return matching file associations |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **render_file_template**
> file_type render_file_template(file_template_id, file_template_render_request)

Render a file template

Renders a file template, applying the static and request arguments to the contents of the template. If the backing file does not exist, this will return a 404 indicating so. If the input is missing a required parameter, this will return a 400. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.file_template_render_request import FileTemplateRenderRequest
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_template_id = "1234" # str | file_template_id in path
    file_template_render_request = FileTemplateRenderRequest(
        template_arguments=[
            FileTemplateArgument(
                name=FileTemplateParameterName("api_key"),
                value=None,
            ),
        ],
        org_id="123",
        resource_information=FileTemplateResourceInfo(
            org_id="123",
            resource_id="123",
            name="my-application",
            uri="postgresql://database-1.databases.remote.anyx.cloud:443/database-1",
            resource_type="database",
            user_resource_info=UserResourceAccessInfoStatus(
                user_id="tuU7smH86zAXMl76sua6xQ",
                org_id="IAsl3dl40aSsfLKiU76",
                org_name="egov",
                parent_org_id="G99q3lasls29wsk",
                parent_org_name="root",
                resource_id="123",
                resource_name="public",
                resource_type="fileshare",
                resource_uri="https://share.cloud.egov.city/public",
                access_level="granted",
                roles=["owner","viewer"],
                display_info=DisplayInfo(
                    icons=[
                        Icon(
                            uri="https://storage.googleapis.com/agilicus/logo.svg",
                            purposes=[
                                IconPurpose("agilicus-launcher"),
                            ],
                            dimensions=IconDimensions(
                                width=32,
                                height=32,
                            ),
                        ),
                    ],
                    hide="no",
                ),
            ),
        ),
        user_information=User(),
        as_attachment=True,
    ) # FileTemplateRenderRequest | 

    # example passing only required values which don't have defaults set
    try:
        # Render a file template
        api_response = api_instance.render_file_template(file_template_id, file_template_render_request)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->render_file_template: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_template_id** | **str**| file_template_id in path |
 **file_template_render_request** | [**FileTemplateRenderRequest**](FileTemplateRenderRequest.md)|  |

### Return type

**file_type**

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: */*, application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Template rendered. &#x60;content_type&#x60; depends on value provided in template. |  -  |
**400** | The request is invalid |  -  |
**404** | The file template or backing file is missing |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_file**
> FileSummary replace_file(file_id, file)

Update a file

Update a file

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.file_summary import FileSummary
from agilicus_api.model.file import File
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_id = "1234" # str | file_id path
    file = File(
        name=FileName("Alice"),
        tag="theme",
        label="label_example",
        visibility=FileVisibility("private"),
        region=StorageRegion("ca"),
        lock=True,
        operstatus=ObjectOperStatus("active"),
    ) # File | Upload file request
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Update a file
        api_response = api_instance.replace_file(file_id, file)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->replace_file: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Update a file
        api_response = api_instance.replace_file(file_id, file, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->replace_file: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_id** | **str**| file_id path |
 **file** | [**File**](File.md)| Upload file request |
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**FileSummary**](FileSummary.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | File was updated |  -  |
**404** | File does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_file_template**
> FileTemplate replace_file_template(file_template_id)

update a file template

update a file template

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.error_message import ErrorMessage
from agilicus_api.model.file_template import FileTemplate
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_template_id = "1234" # str | file_template_id in path
    file_template = FileTemplate(
        metadata=MetadataWithId(),
        spec=FileTemplateSpec(
            template_parameters=[
                FileTemplateParameter(
                    name=FileTemplateParameterName("api_key"),
                    input_hint="agilicus.api_key.",
                ),
            ],
            template_content_type="application/zip",
            default_arguments=[
                FileTemplateArgument(
                    name=FileTemplateParameterName("api_key"),
                    value=None,
                ),
            ],
            purpose="project-file",
            template_file="123",
            org_id="123",
            descriptive_text="Project File",
            associated_objects=[
                FileTemplateAssociation(
                    object_id="123",
                    object_type=ObjectType("desktop"),
                    descriptive_text="descriptive_text_example",
                ),
            ],
            rendered_file_name="my-config.txt",
            delimiter="%",
        ),
    ) # FileTemplate |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # update a file template
        api_response = api_instance.replace_file_template(file_template_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->replace_file_template: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # update a file template
        api_response = api_instance.replace_file_template(file_template_id, file_template=file_template)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->replace_file_template: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_template_id** | **str**| file_template_id in path |
 **file_template** | [**FileTemplate**](FileTemplate.md)|  | [optional]

### Return type

[**FileTemplate**](FileTemplate.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated FileTemplate |  -  |
**400** | The request is invalid |  -  |
**404** | FileTemplate does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_public_file_org_link**
> PublicFileOrgLink replace_public_file_org_link(public_file_org_link_id, public_file_org_link)

Replace a public file org link

Replace a public file org link

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.public_file_org_link import PublicFileOrgLink
from agilicus_api.model.error_message import ErrorMessage
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    public_file_org_link_id = "1234" # str | public file org link id in path
    public_file_org_link = PublicFileOrgLink(
        metadata=MetadataWithId(),
        spec=PublicFileOrgLinkSpec(
            file_tag="theme",
            link_org_id=None,
            target_org_id=None,
        ),
    ) # PublicFileOrgLink | The link to update
    link_org_id = "1234" # str | Search for the Organisation that is linked to another (optional)
    org_id = "1234" # str | Organisation Unique identifier (optional)

    # example passing only required values which don't have defaults set
    try:
        # Replace a public file org link
        api_response = api_instance.replace_public_file_org_link(public_file_org_link_id, public_file_org_link)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->replace_public_file_org_link: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Replace a public file org link
        api_response = api_instance.replace_public_file_org_link(public_file_org_link_id, public_file_org_link, link_org_id=link_org_id, org_id=org_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->replace_public_file_org_link: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **public_file_org_link_id** | **str**| public file org link id in path |
 **public_file_org_link** | [**PublicFileOrgLink**](PublicFileOrgLink.md)| The link to update |
 **link_org_id** | **str**| Search for the Organisation that is linked to another | [optional]
 **org_id** | **str**| Organisation Unique identifier | [optional]

### Return type

[**PublicFileOrgLink**](PublicFileOrgLink.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | link updated |  -  |
**404** | link not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reupload_file**
> FileSummary reupload_file(file_id, org_id, file_zip)

Upload a new version of a file

Replace a file entirely by uploading new contents

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import files_api
from agilicus_api.model.file_summary import FileSummary
from pprint import pprint
# Defining the host is optional and defaults to https://api.agilicus.com
# See configuration.py for a list of all supported configuration parameters.
configuration = agilicus_api.Configuration(
    host = "https://api.agilicus.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): token-valid
configuration = agilicus_api.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)

# Enter a context with an instance of the API client
with agilicus_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api.FilesApi(api_client)
    file_id = "1234" # str | file_id path
    org_id = "123" # str | Unique identifier
    file_zip = open('/path/to/file', 'rb') # file_type | The contents of the file in binary format

    # example passing only required values which don't have defaults set
    try:
        # Upload a new version of a file
        api_response = api_instance.reupload_file(file_id, org_id, file_zip)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling FilesApi->reupload_file: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_id** | **str**| file_id path |
 **org_id** | **str**| Unique identifier |
 **file_zip** | **file_type**| The contents of the file in binary format |

### Return type

[**FileSummary**](FileSummary.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | File was updated |  -  |
**404** | File does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

