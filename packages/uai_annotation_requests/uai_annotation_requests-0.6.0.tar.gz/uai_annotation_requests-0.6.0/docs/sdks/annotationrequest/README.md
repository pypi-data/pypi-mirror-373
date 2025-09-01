# AnnotationRequest
(*annotation_request*)

## Overview

### Available Operations

* [create](#create) - Create a new annotation request
* [get](#get) - Get annotation request
* [get_filtered](#get_filtered) - Get annotation requests filtered by projectId and phase.
* [get_by_annotation_request_id](#get_by_annotation_request_id) - Get annotation request by the annotation request ID
* [restart_annotation_request](#restart_annotation_request) - Restart the data intake for one or more clips
* [get_exported_annotations](#get_exported_annotations) - Request the download URLs for the result annotations.

## create

This endpoint creates a new annotation request.

An annotation request can contain one or more clips
that should be part of the same annotation batch.

The annotation request and the clips have reference fields where
you must provide your own reference that is used to identify
the data in the client system. This reference is used to
map data between the UAI system and the client system.

For UAI to be able to process the data of the annotation request,
data must be made available to the UAI system. This is done by a data intake
step in the UAI system which makes data from the client
available to UAI based on the requirements of the integration
and project. To enable integration specific data exchanges
the API allows the `clips[].parameters` field of the clip to be
defined per project. If applicable, a clip parameters schema is agreed upon
together with UAI for the project.

Requests to the UAI API must include an authorization token.
To request a token the client must authenticate against a token endpoint
with the `client_id` and `client_secret` provided by UAI.
If the token request is successful a JSON response is returned
with an access token that can be used to authorize and call the
UAI API.

**Example call to token endpoint and response:**

```
curl -X POST https://signin.services.understand.ai/auth/realms/understand.ai/protocol/openid-connect/token \
  -H "content-type: application/x-www-form-urlencoded" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" \
  -d "grant_type=client_credentials"
{
  "access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIxxxxxxx....w",
  "expires_in":900,"refresh_expires_in":0,
  "token_type":"Bearer",
  "not-before-policy":0,
  "scope":"external-api-audience"
}
```

### Example Usage

<!-- UsageSnippet language="python" operationID="Create" method="post" path="/v1/projects/{projectId}/annotation-requests" -->
```python
from uai_annotation_requests import UaiAnnotationRequests


with UaiAnnotationRequests(
    uai_oauth2="<YOUR_UAI_OAUTH2_HERE>",
) as uar_client:

    res = uar_client.annotation_request.create(project_id="<id>", clips=[
        {
            "clip_reference_id": "<id>",
        },
    ], request_reference_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                                                                                                                                                                                                                                                                                | Type                                                                                                                                                                                                                                                                                                                                                     | Required                                                                                                                                                                                                                                                                                                                                                 | Description                                                                                                                                                                                                                                                                                                                                              |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `project_id`                                                                                                                                                                                                                                                                                                                                             | *str*                                                                                                                                                                                                                                                                                                                                                    | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                                       | The ID of the project to process the annotation request. Provided by UAI.                                                                                                                                                                                                                                                                                |
| `clips`                                                                                                                                                                                                                                                                                                                                                  | List[[models.CreateClipDTO](../../models/createclipdto.md)]                                                                                                                                                                                                                                                                                              | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                                       | The clips to be annotated<br/>in the request                                                                                                                                                                                                                                                                                                             |
| `request_reference_id`                                                                                                                                                                                                                                                                                                                                   | *str*                                                                                                                                                                                                                                                                                                                                                    | :heavy_check_mark:                                                                                                                                                                                                                                                                                                                                       | A reference to<br/>data in the client system.<br/><br/>The value of this field must be<br/>unique per project.                                                                                                                                                                                                                                           |
| `callback_url`                                                                                                                                                                                                                                                                                                                                           | *Optional[str]*                                                                                                                                                                                                                                                                                                                                          | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                                       | An optional callback URL to send<br/>annotation request updates to.                                                                                                                                                                                                                                                                                      |
| `priority`                                                                                                                                                                                                                                                                                                                                               | *Optional[int]*                                                                                                                                                                                                                                                                                                                                          | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                                       | An optional priority value to use<br/>for the annotation request.<br/><br/>The priority of an annotation request<br/>determines the order of processing within<br/>the project.<br/><br/>Annotation requests with higher priority<br/>will be processed earlier than annotation<br/>requests with lower priority.<br/><br/>By default, the priority is 0 for all<br/>annotation requests in the project. |
| `display_name`                                                                                                                                                                                                                                                                                                                                           | *Optional[str]*                                                                                                                                                                                                                                                                                                                                          | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                                       | An optional display name<br/>to show in UAI tooling                                                                                                                                                                                                                                                                                                      |
| `retries`                                                                                                                                                                                                                                                                                                                                                | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                                                                                                                                                                                                                                                         | :heavy_minus_sign:                                                                                                                                                                                                                                                                                                                                       | Configuration to override the default retry behavior of the client.                                                                                                                                                                                                                                                                                      |

### Response

**[models.AnnotationRequestDTO](../../models/annotationrequestdto.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| models.APIError | 4XX, 5XX        | \*/\*           |

## get

Get an annotation request by different IDs. It is recommended to get
the annotation request by the annotationRequestId if possible.

The current progress of an annotation request can be observed by
the phase field. When the phase is "COMPLETE" the annotations are
ready to be downloaded.

### Example Usage

<!-- UsageSnippet language="python" operationID="Get" method="get" path="/v1/projects/{projectId}/annotation-requests" -->
```python
import uai_annotation_requests
from uai_annotation_requests import UaiAnnotationRequests


with UaiAnnotationRequests(
    uai_oauth2="<YOUR_UAI_OAUTH2_HERE>",
) as uar_client:

    res = uar_client.annotation_request.get(project_id="<id>", field=uai_annotation_requests.FilterField.REQUEST_REFERENCE_ID, value="<value>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `project_id`                                                                       | *str*                                                                              | :heavy_check_mark:                                                                 | The ID of the project which is processing the annotation request. Provided by UAI. |
| `field`                                                                            | [models.FilterField](../../models/filterfield.md)                                  | :heavy_check_mark:                                                                 | The field to get the annotation request by.                                        |
| `value`                                                                            | *str*                                                                              | :heavy_check_mark:                                                                 | The value of the field to get the annotation request by.                           |
| `retries`                                                                          | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                   | :heavy_minus_sign:                                                                 | Configuration to override the default retry behavior of the client.                |

### Response

**[models.AnnotationRequestDTO](../../models/annotationrequestdto.md)**

### Errors

| Error Type                          | Status Code                         | Content Type                        |
| ----------------------------------- | ----------------------------------- | ----------------------------------- |
| models.AnnotationRequestNotFoundDTO | 404                                 | application/json                    |
| models.APIError                     | 4XX, 5XX                            | \*/\*                               |

## get_filtered

Get annotation requests that match the filter criteria.

### Example Usage

<!-- UsageSnippet language="python" operationID="GetFiltered" method="get" path="/v1/projects/{projectId}/annotation-requests/filtered" -->
```python
from uai_annotation_requests import UaiAnnotationRequests


with UaiAnnotationRequests(
    uai_oauth2="<YOUR_UAI_OAUTH2_HERE>",
) as uar_client:

    res = uar_client.annotation_request.get_filtered(project_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                                                                 | Type                                                                                                                      | Required                                                                                                                  | Description                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `project_id`                                                                                                              | *str*                                                                                                                     | :heavy_check_mark:                                                                                                        | The ID of the project which is processing the annotation request. Provided by UAI.                                        |
| `phase`                                                                                                                   | [Optional[models.AnnotationRequestPhase]](../../models/annotationrequestphase.md)                                         | :heavy_minus_sign:                                                                                                        | Optional filter for phase. If set only annotation requests currently in the specified<br/>phase are returned in the response. |
| `retries`                                                                                                                 | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                                                          | :heavy_minus_sign:                                                                                                        | Configuration to override the default retry behavior of the client.                                                       |

### Response

**[List[models.AnnotationRequestCondensedDTO]](../../models/.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| models.APIError | 4XX, 5XX        | \*/\*           |

## get_by_annotation_request_id

Get an annotation request by the annotation request ID.

The current progress of an annotation request can be observed by
the phase field. When the phase is "COMPLETE" the annotations are
ready to be downloaded.

### Example Usage

<!-- UsageSnippet language="python" operationID="GetByAnnotationRequestId" method="get" path="/v1/projects/{projectId}/annotation-requests/{annotationRequestId}" -->
```python
from uai_annotation_requests import UaiAnnotationRequests


with UaiAnnotationRequests(
    uai_oauth2="<YOUR_UAI_OAUTH2_HERE>",
) as uar_client:

    res = uar_client.annotation_request.get_by_annotation_request_id(project_id="<id>", annotation_request_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `project_id`                                                                       | *str*                                                                              | :heavy_check_mark:                                                                 | The ID of the project which is processing the annotation request. Provided by UAI. |
| `annotation_request_id`                                                            | *str*                                                                              | :heavy_check_mark:                                                                 | N/A                                                                                |
| `retries`                                                                          | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                   | :heavy_minus_sign:                                                                 | Configuration to override the default retry behavior of the client.                |

### Response

**[models.AnnotationRequestDTO](../../models/annotationrequestdto.md)**

### Errors

| Error Type                          | Status Code                         | Content Type                        |
| ----------------------------------- | ----------------------------------- | ----------------------------------- |
| models.AnnotationRequestNotFoundDTO | 404                                 | application/json                    |
| models.APIError                     | 4XX, 5XX                            | \*/\*                               |

## restart_annotation_request

Restart the data intake procedure for one or more clips of an annotation request.

If a clip has faulty data and fails to be imported in the UAI system it is possible
to replace the data and restart the data intake procedure using this endpoint.

### Example Usage

<!-- UsageSnippet language="python" operationID="RestartAnnotationRequest" method="post" path="/v1/projects/{projectId}/annotation-requests/{annotationRequestId}/restart" -->
```python
from uai_annotation_requests import UaiAnnotationRequests


with UaiAnnotationRequests(
    uai_oauth2="<YOUR_UAI_OAUTH2_HERE>",
) as uar_client:

    res = uar_client.annotation_request.restart_annotation_request(project_id="<id>", annotation_request_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `project_id`                                                                       | *str*                                                                              | :heavy_check_mark:                                                                 | The ID of the project which is processing the annotation request. Provided by UAI. |
| `annotation_request_id`                                                            | *str*                                                                              | :heavy_check_mark:                                                                 | N/A                                                                                |
| `clip_reference_ids`                                                               | List[*str*]                                                                        | :heavy_minus_sign:                                                                 | N/A                                                                                |
| `retries`                                                                          | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                   | :heavy_minus_sign:                                                                 | Configuration to override the default retry behavior of the client.                |

### Response

**[models.RestartResult](../../models/restartresult.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| models.APIError | 4XX, 5XX        | \*/\*           |

## get_exported_annotations

This endpoint provides a list of downloadable URLs for a
completed annotation request. If the annotation request is not yet
in the COMPLETE phase the response status code will be 404 - not found.

The download URLs will be in the form of Google Cloud Storage signed URLs
that are only valid for a short period of time. If the integration client
fails to download the content within the valid duration new download URLs can be
requested via this endpoint.

### Example Usage

<!-- UsageSnippet language="python" operationID="GetExportedAnnotations" method="get" path="/v1/projects/{projectId}/annotation-requests/{annotationRequestId}/annotations" -->
```python
from uai_annotation_requests import UaiAnnotationRequests


with UaiAnnotationRequests(
    uai_oauth2="<YOUR_UAI_OAUTH2_HERE>",
) as uar_client:

    res = uar_client.annotation_request.get_exported_annotations(project_id="<id>", annotation_request_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                          | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `project_id`                                                                       | *str*                                                                              | :heavy_check_mark:                                                                 | The ID of the project which is processing the annotation request. Provided by UAI. |
| `annotation_request_id`                                                            | *str*                                                                              | :heavy_check_mark:                                                                 | The ID of the annotation request.                                                  |
| `retries`                                                                          | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                   | :heavy_minus_sign:                                                                 | Configuration to override the default retry behavior of the client.                |

### Response

**[models.AnnotationRequestExportReferenceDTO](../../models/annotationrequestexportreferencedto.md)**

### Errors

| Error Type                                | Status Code                               | Content Type                              |
| ----------------------------------------- | ----------------------------------------- | ----------------------------------------- |
| models.AnnotationRequestExportNotReadyDTO | 404                                       | application/json                          |
| models.APIError                           | 4XX, 5XX                                  | \*/\*                                     |