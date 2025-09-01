# CreateRequest


## Fields

| Field                                                                        | Type                                                                         | Required                                                                     | Description                                                                  |
| ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `project_id`                                                                 | *str*                                                                        | :heavy_check_mark:                                                           | The ID of the project to process the annotation request. Provided by UAI.    |
| `create_annotation_request_dto`                                              | [models.CreateAnnotationRequestDTO](../models/createannotationrequestdto.md) | :heavy_check_mark:                                                           | The annotation request parameters                                            |