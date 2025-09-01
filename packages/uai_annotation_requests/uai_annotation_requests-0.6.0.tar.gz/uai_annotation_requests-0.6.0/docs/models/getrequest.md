# GetRequest


## Fields

| Field                                                                              | Type                                                                               | Required                                                                           | Description                                                                        |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `project_id`                                                                       | *str*                                                                              | :heavy_check_mark:                                                                 | The ID of the project which is processing the annotation request. Provided by UAI. |
| `field`                                                                            | [models.FilterField](../models/filterfield.md)                                     | :heavy_check_mark:                                                                 | The field to get the annotation request by.                                        |
| `value`                                                                            | *str*                                                                              | :heavy_check_mark:                                                                 | The value of the field to get the annotation request by.                           |