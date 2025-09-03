# Clips
(*clips*)

## Overview

### Available Operations

* [get_clips](#get_clips) - Get clips in the project filtered by clip reference ids and
states.

For example, querying for clips with state 'Exported'
lists all the clips that have annotations to fetch.

Combinding the filters state and isExportDownloaded
makes it possible to list all the clips that are exported
and haven't yet been downloaded by the client, ex:
`?state=Exported&isExportDownloade=false`
* [get_annotations](#get_annotations) - Get annotations for a clip.

The clip must be in state Exported.

## get_clips

Get clips in the project filtered by clip reference ids and
states.

For example, querying for clips with state 'Exported'
lists all the clips that have annotations to fetch.

Combinding the filters state and isExportDownloaded
makes it possible to list all the clips that are exported
and haven't yet been downloaded by the client, ex:
`?state=Exported&isExportDownloade=false`

### Example Usage

<!-- UsageSnippet language="python" operationID="GetClips" method="get" path="/v1/projects/{projectId}/clips" -->
```python
from uai_annotation_requests import UaiAnnotationRequests


with UaiAnnotationRequests(
    uai_oauth2="<YOUR_UAI_OAUTH2_HERE>",
) as uar_client:

    res = uar_client.clips.get_clips(project_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                                             | Type                                                                                  | Required                                                                              | Description                                                                           |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `project_id`                                                                          | *str*                                                                                 | :heavy_check_mark:                                                                    | the project id to get clips for                                                       |
| `annotation_request_id`                                                               | List[*str*]                                                                           | :heavy_minus_sign:                                                                    | filter clips by annotation request ids                                                |
| `state`                                                                               | List[[models.ClipBusinessState](../../models/clipbusinessstate.md)]                   | :heavy_minus_sign:                                                                    | filter clips by clip states                                                           |
| `clip_reference_id`                                                                   | List[*str*]                                                                           | :heavy_minus_sign:                                                                    | filter by clip reference ids                                                          |
| `is_export_downloaded`                                                                | *Optional[bool]*                                                                      | :heavy_minus_sign:                                                                    | filter clips by if the exported annotations are previously downloaded or not          |
| `sort_by`                                                                             | [Optional[models.SortBy]](../../models/sortby.md)                                     | :heavy_minus_sign:                                                                    | sort the clips                                                                        |
| `sort_order`                                                                          | [Optional[models.SortOrder]](../../models/sortorder.md)                               | :heavy_minus_sign:                                                                    | ascending or descending sort order                                                    |
| `skip`                                                                                | *Optional[int]*                                                                       | :heavy_minus_sign:                                                                    | skip the N first clips, can be used in combination with limit to implement pagination |
| `limit`                                                                               | *Optional[int]*                                                                       | :heavy_minus_sign:                                                                    | limits the output to N number of clips                                                |
| `retries`                                                                             | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)                      | :heavy_minus_sign:                                                                    | Configuration to override the default retry behavior of the client.                   |

### Response

**[models.ClipsList](../../models/clipslist.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| models.APIError | 4XX, 5XX        | \*/\*           |

## get_annotations

Get annotations for a clip.

The clip must be in state Exported.

### Example Usage

<!-- UsageSnippet language="python" operationID="GetAnnotations" method="get" path="/v1/projects/{projectId}/clips/{clipReferenceId}/annotations" -->
```python
from uai_annotation_requests import UaiAnnotationRequests


with UaiAnnotationRequests(
    uai_oauth2="<YOUR_UAI_OAUTH2_HERE>",
) as uar_client:

    res = uar_client.clips.get_annotations(project_id="<id>", clip_reference_id="<id>")

    # Handle response
    print(res)

```

### Parameters

| Parameter                                                           | Type                                                                | Required                                                            | Description                                                         |
| ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `project_id`                                                        | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `clip_reference_id`                                                 | *str*                                                               | :heavy_check_mark:                                                  | N/A                                                                 |
| `retries`                                                           | [Optional[utils.RetryConfig]](../../models/utils/retryconfig.md)    | :heavy_minus_sign:                                                  | Configuration to override the default retry behavior of the client. |

### Response

**[models.ClipExportURL](../../models/clipexporturl.md)**

### Errors

| Error Type      | Status Code     | Content Type    |
| --------------- | --------------- | --------------- |
| models.APIError | 4XX, 5XX        | \*/\*           |