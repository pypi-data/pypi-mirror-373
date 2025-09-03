# agilicus_api.LicensingApi

All URIs are relative to *https://api.agilicus.com*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_hypothetical_license_details_query**](LicensingApi.md#create_hypothetical_license_details_query) | **POST** /v1/license_details/hypothetical | Query a hypothetical set of license details
[**create_license**](LicensingApi.md#create_license) | **POST** /v1/licenses | Create a license
[**create_product_table_version**](LicensingApi.md#create_product_table_version) | **POST** /v1/product_table_versions | Create a product table version
[**delete_license**](LicensingApi.md#delete_license) | **DELETE** /v1/licenses/{license_id} | Delete a license
[**delete_product_table_version**](LicensingApi.md#delete_product_table_version) | **DELETE** /v1/product_table_versions/{product_table_version_id} | Delete a product table version
[**get_license**](LicensingApi.md#get_license) | **GET** /v1/licenses/{license_id} | Get a single license
[**get_product_table_version**](LicensingApi.md#get_product_table_version) | **GET** /v1/product_table_versions/{product_table_version_id} | Get a single product table version
[**list_license_details**](LicensingApi.md#list_license_details) | **GET** /v1/license_details | Get all license details
[**list_license_evaluation_contexts**](LicensingApi.md#list_license_evaluation_contexts) | **GET** /v1/licenses/evaluation_contexts | Get license evaluation context
[**list_licenses**](LicensingApi.md#list_licenses) | **GET** /v1/licenses | Get all licenses
[**list_product_table_versions**](LicensingApi.md#list_product_table_versions) | **GET** /v1/product_table_versions | Get all product table versions
[**replace_license**](LicensingApi.md#replace_license) | **PUT** /v1/licenses/{license_id} | Create or update a license
[**replace_product_table_version**](LicensingApi.md#replace_product_table_version) | **PUT** /v1/product_table_versions/{product_table_version_id} | Create or update a product table version


# **create_hypothetical_license_details_query**
> HypotheticalLicenseDetails create_hypothetical_license_details_query(hypothetical_license_details_query)

Query a hypothetical set of license details

Get all per-org license details matching the query. This will return the actual constraints available to an organisation, taking into account their product, the hypothetical version of the product table, and any overrides applied to their organisation. Multiple organisations' constraints may be returned at a time. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.hypothetical_license_details import HypotheticalLicenseDetails
from agilicus_api.model.hypothetical_license_details_query import HypotheticalLicenseDetailsQuery
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
    api_instance = licensing_api.LicensingApi(api_client)
    hypothetical_license_details_query = HypotheticalLicenseDetailsQuery(
        product_table_version=ProductTableVersion(
            metadata=MetadataWithId(),
            spec=ProductTableVersionSpec(
                version=ProductTableVersionString("2025-06-13.0"),
                product_table=ProductTable(
                    products=[
                        LicensedProduct(
                            name=LicensedProductName("Standard"),
                            included_features=[
                                LicensedFeatureName("Desktops"),
                            ],
                            license_constraints=[
                                LicenseConstraint(
                                    name=LicenseConstraintName("desktops_below_max"),
                                    expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                                    priority=0,
                                    comment="Uses the max_desktops from the product to enforce a limit on desktops",
                                ),
                            ],
                            constraint_variables=LicenseConstraintVariables(),
                        ),
                    ],
                    features=[
                        LicensedFeature(
                            name=LicensedFeatureName("Desktops"),
                            license_constraints=[
                                LicenseConstraint(
                                    name=LicenseConstraintName("desktops_below_max"),
                                    expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                                    priority=0,
                                    comment="Uses the max_desktops from the product to enforce a limit on desktops",
                                ),
                            ],
                            constraint_variables=LicenseConstraintVariables(),
                        ),
                    ],
                    constraint_variables=LicenseConstraintVariables(),
                    global_constraints=[
                        LicenseConstraint(
                            name=LicenseConstraintName("desktops_below_max"),
                            expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                            priority=0,
                            comment="Uses the max_desktops from the product to enforce a limit on desktops",
                        ),
                    ],
                ),
                published=True,
            ),
        ),
        license_ids=[
            "123",
        ],
        constrain_to_version=ProductTableVersionString("2025-06-13.0"),
    ) # HypotheticalLicenseDetailsQuery | 

    # example passing only required values which don't have defaults set
    try:
        # Query a hypothetical set of license details
        api_response = api_instance.create_hypothetical_license_details_query(hypothetical_license_details_query)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->create_hypothetical_license_details_query: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hypothetical_license_details_query** | [**HypotheticalLicenseDetailsQuery**](HypotheticalLicenseDetailsQuery.md)|  |

### Return type

[**HypotheticalLicenseDetails**](HypotheticalLicenseDetails.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Matching license details returned |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_license**
> License create_license(license)

Create a license

Create a license

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.license import License
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
    api_instance = licensing_api.LicensingApi(api_client)
    license = License(
        metadata=MetadataWithId(),
        spec=LicenseSpec(
            product_table_version=ProductTableVersionString("2025-06-13.0"),
            product_name=LicensedProductName("Standard"),
            license_constraints=[
                LicenseConstraint(
                    name=LicenseConstraintName("desktops_below_max"),
                    expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                    priority=0,
                    comment="Uses the max_desktops from the product to enforce a limit on desktops",
                ),
            ],
            constraint_variables=LicenseConstraintVariables(),
        ),
    ) # License | 

    # example passing only required values which don't have defaults set
    try:
        # Create a license
        api_response = api_instance.create_license(license)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->create_license: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **license** | [**License**](License.md)|  |

### Return type

[**License**](License.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New license created |  -  |
**400** | license was malformed |  -  |
**409** | license already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_product_table_version**
> ProductTableVersion create_product_table_version(product_table_version)

Create a product table version

Create a product table version

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.product_table_version import ProductTableVersion
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
    api_instance = licensing_api.LicensingApi(api_client)
    product_table_version = ProductTableVersion(
        metadata=MetadataWithId(),
        spec=ProductTableVersionSpec(
            version=ProductTableVersionString("2025-06-13.0"),
            product_table=ProductTable(
                products=[
                    LicensedProduct(
                        name=LicensedProductName("Standard"),
                        included_features=[
                            LicensedFeatureName("Desktops"),
                        ],
                        license_constraints=[
                            LicenseConstraint(
                                name=LicenseConstraintName("desktops_below_max"),
                                expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                                priority=0,
                                comment="Uses the max_desktops from the product to enforce a limit on desktops",
                            ),
                        ],
                        constraint_variables=LicenseConstraintVariables(),
                    ),
                ],
                features=[
                    LicensedFeature(
                        name=LicensedFeatureName("Desktops"),
                        license_constraints=[
                            LicenseConstraint(
                                name=LicenseConstraintName("desktops_below_max"),
                                expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                                priority=0,
                                comment="Uses the max_desktops from the product to enforce a limit on desktops",
                            ),
                        ],
                        constraint_variables=LicenseConstraintVariables(),
                    ),
                ],
                constraint_variables=LicenseConstraintVariables(),
                global_constraints=[
                    LicenseConstraint(
                        name=LicenseConstraintName("desktops_below_max"),
                        expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                        priority=0,
                        comment="Uses the max_desktops from the product to enforce a limit on desktops",
                    ),
                ],
            ),
            published=True,
        ),
    ) # ProductTableVersion | 

    # example passing only required values which don't have defaults set
    try:
        # Create a product table version
        api_response = api_instance.create_product_table_version(product_table_version)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->create_product_table_version: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **product_table_version** | [**ProductTableVersion**](ProductTableVersion.md)|  |

### Return type

[**ProductTableVersion**](ProductTableVersion.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | New product table version created |  -  |
**400** | Product Table Version was malformed |  -  |
**409** | product table version already exists |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_license**
> delete_license(license_id)

Delete a license

Delete a license

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
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
    api_instance = licensing_api.LicensingApi(api_client)
    license_id = "1234" # str | A license id

    # example passing only required values which don't have defaults set
    try:
        # Delete a license
        api_instance.delete_license(license_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->delete_license: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **license_id** | **str**| A license id |

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
**204** | license has been deleted |  -  |
**400** | A subscription still refers to this license. |  -  |
**404** | license does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_product_table_version**
> delete_product_table_version(product_table_version_id)

Delete a product table version

Delete a product table version

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
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
    api_instance = licensing_api.LicensingApi(api_client)
    product_table_version_id = "1234" # str | A product table version id

    # example passing only required values which don't have defaults set
    try:
        # Delete a product table version
        api_instance.delete_product_table_version(product_table_version_id)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->delete_product_table_version: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **product_table_version_id** | **str**| A product table version id |

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
**204** | product table version has been deleted |  -  |
**400** | A license still refers to this product table version. |  -  |
**404** | product table version does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_license**
> License get_license(license_id)

Get a single license

Get a single license

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.license import License
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
    api_instance = licensing_api.LicensingApi(api_client)
    license_id = "1234" # str | A license id

    # example passing only required values which don't have defaults set
    try:
        # Get a single license
        api_response = api_instance.get_license(license_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->get_license: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **license_id** | **str**| A license id |

### Return type

[**License**](License.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return license |  -  |
**404** | license does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_product_table_version**
> ProductTableVersion get_product_table_version(product_table_version_id)

Get a single product table version

Get a single product table version

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.product_table_version import ProductTableVersion
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
    api_instance = licensing_api.LicensingApi(api_client)
    product_table_version_id = "1234" # str | A product table version id

    # example passing only required values which don't have defaults set
    try:
        # Get a single product table version
        api_response = api_instance.get_product_table_version(product_table_version_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->get_product_table_version: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **product_table_version_id** | **str**| A product table version id |

### Return type

[**ProductTableVersion**](ProductTableVersion.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return product table version |  -  |
**404** | product table version does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_license_details**
> ListLicenseDetailsResponse list_license_details()

Get all license details

Get all per-org license details matching the query. This will return the actual constraints available to an organisation, taking into account their product, version of the product table, and any overrides applied to their organisation. Multiple organisations' constraints may be returned at a time, and paged through using page_at_id. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.list_license_details_response import ListLicenseDetailsResponse
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
    api_instance = licensing_api.LicensingApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    license_id = "1234" # str | A license id (optional)
    license_ids = ["1234"] # [str] | A list of license ids (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all license details
        api_response = api_instance.list_license_details(limit=limit, org_id=org_id, license_id=license_id, license_ids=license_ids, page_at_id=page_at_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->list_license_details: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **license_id** | **str**| A license id | [optional]
 **license_ids** | **[str]**| A list of license ids | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]

### Return type

[**ListLicenseDetailsResponse**](ListLicenseDetailsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Matching licenses returned |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_license_evaluation_contexts**
> ListLicenseEvaluationContextsResponse list_license_evaluation_contexts()

Get license evaluation context

Get all per-org license evaluation input matching the query. This will return the context dictionary to pass into the evaluation of a license. Multiple organisations' input may be returned at a time, and paged through using page_at_id. 

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.list_license_evaluation_contexts_response import ListLicenseEvaluationContextsResponse
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
    api_instance = licensing_api.LicensingApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    org_id = "1234" # str | Organisation Unique identifier (optional)
    license_id = "1234" # str | A license id (optional)
    license_ids = ["1234"] # [str] | A list of license ids (optional)
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get license evaluation context
        api_response = api_instance.list_license_evaluation_contexts(limit=limit, org_id=org_id, license_id=license_id, license_ids=license_ids, page_at_id=page_at_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->list_license_evaluation_contexts: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **org_id** | **str**| Organisation Unique identifier | [optional]
 **license_id** | **str**| A license id | [optional]
 **license_ids** | **[str]**| A list of license ids | [optional]
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]

### Return type

[**ListLicenseEvaluationContextsResponse**](ListLicenseEvaluationContextsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Matching licenses returned |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_licenses**
> ListLicensesResponse list_licenses()

Get all licenses

Get all Licenses matching the query

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.list_licenses_response import ListLicensesResponse
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
    api_instance = licensing_api.LicensingApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    page_at_id = "foo@example.com" # str | Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the `page_at_id` field from the list response.  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all licenses
        api_response = api_instance.list_licenses(limit=limit, page_at_id=page_at_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->list_licenses: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **page_at_id** | **str**| Pagination based query with the id as the key. To get the initial entries supply an empty string. On subsequent requests, supply the &#x60;page_at_id&#x60; field from the list response.  | [optional]

### Return type

[**ListLicensesResponse**](ListLicensesResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Matching licenses returned |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_product_table_versions**
> ListProductTableVersionsResponse list_product_table_versions()

Get all product table versions

Get all product table versions matching the query

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.list_product_table_versions_response import ListProductTableVersionsResponse
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
    api_instance = licensing_api.LicensingApi(api_client)
    limit = 1 # int | limit the number of rows in the response (optional) if omitted the server will use the default value of 500
    version = "2025-05-03T00:00:00.000Z" # str | Query based on a version (optional)
    page_at_version = "2025-05-03T00:00:00.000Z" # str | Page based on a version (optional)
    published = True # bool | Query based on a whether something is published (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Get all product table versions
        api_response = api_instance.list_product_table_versions(limit=limit, version=version, page_at_version=page_at_version, published=published)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->list_product_table_versions: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| limit the number of rows in the response | [optional] if omitted the server will use the default value of 500
 **version** | **str**| Query based on a version | [optional]
 **page_at_version** | **str**| Page based on a version | [optional]
 **published** | **bool**| Query based on a whether something is published | [optional]

### Return type

[**ListProductTableVersionsResponse**](ListProductTableVersionsResponse.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Matching product table versions returned |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_license**
> License replace_license(license_id)

Create or update a license

Update a license

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.license import License
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
    api_instance = licensing_api.LicensingApi(api_client)
    license_id = "1234" # str | A license id
    license = License(
        metadata=MetadataWithId(),
        spec=LicenseSpec(
            product_table_version=ProductTableVersionString("2025-06-13.0"),
            product_name=LicensedProductName("Standard"),
            license_constraints=[
                LicenseConstraint(
                    name=LicenseConstraintName("desktops_below_max"),
                    expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                    priority=0,
                    comment="Uses the max_desktops from the product to enforce a limit on desktops",
                ),
            ],
            constraint_variables=LicenseConstraintVariables(),
        ),
    ) # License |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Create or update a license
        api_response = api_instance.replace_license(license_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->replace_license: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Create or update a license
        api_response = api_instance.replace_license(license_id, license=license)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->replace_license: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **license_id** | **str**| A license id |
 **license** | [**License**](License.md)|  | [optional]

### Return type

[**License**](License.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated license |  -  |
**404** | License does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replace_product_table_version**
> ProductTableVersion replace_product_table_version(product_table_version_id)

Create or update a product table version

Update a product table version

### Example

* Bearer (JWT) Authentication (token-valid):
```python
import time
import agilicus_api
from agilicus_api.api import licensing_api
from agilicus_api.model.product_table_version import ProductTableVersion
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
    api_instance = licensing_api.LicensingApi(api_client)
    product_table_version_id = "1234" # str | A product table version id
    product_table_version = ProductTableVersion(
        metadata=MetadataWithId(),
        spec=ProductTableVersionSpec(
            version=ProductTableVersionString("2025-06-13.0"),
            product_table=ProductTable(
                products=[
                    LicensedProduct(
                        name=LicensedProductName("Standard"),
                        included_features=[
                            LicensedFeatureName("Desktops"),
                        ],
                        license_constraints=[
                            LicenseConstraint(
                                name=LicenseConstraintName("desktops_below_max"),
                                expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                                priority=0,
                                comment="Uses the max_desktops from the product to enforce a limit on desktops",
                            ),
                        ],
                        constraint_variables=LicenseConstraintVariables(),
                    ),
                ],
                features=[
                    LicensedFeature(
                        name=LicensedFeatureName("Desktops"),
                        license_constraints=[
                            LicenseConstraint(
                                name=LicenseConstraintName("desktops_below_max"),
                                expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                                priority=0,
                                comment="Uses the max_desktops from the product to enforce a limit on desktops",
                            ),
                        ],
                        constraint_variables=LicenseConstraintVariables(),
                    ),
                ],
                constraint_variables=LicenseConstraintVariables(),
                global_constraints=[
                    LicenseConstraint(
                        name=LicenseConstraintName("desktops_below_max"),
                        expression=LicenseConstraintExpression("subscription.usage.num_desktops < 10"),
                        priority=0,
                        comment="Uses the max_desktops from the product to enforce a limit on desktops",
                    ),
                ],
            ),
            published=True,
        ),
    ) # ProductTableVersion |  (optional)

    # example passing only required values which don't have defaults set
    try:
        # Create or update a product table version
        api_response = api_instance.replace_product_table_version(product_table_version_id)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->replace_product_table_version: %s\n" % e)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Create or update a product table version
        api_response = api_instance.replace_product_table_version(product_table_version_id, product_table_version=product_table_version)
        pprint(api_response)
    except agilicus_api.ApiException as e:
        print("Exception when calling LicensingApi->replace_product_table_version: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **product_table_version_id** | **str**| A product table version id |
 **product_table_version** | [**ProductTableVersion**](ProductTableVersion.md)|  | [optional]

### Return type

[**ProductTableVersion**](ProductTableVersion.md)

### Authorization

[token-valid](../README.md#token-valid)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Return updated product table version |  -  |
**404** | ProductTableVersion does not exist |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

