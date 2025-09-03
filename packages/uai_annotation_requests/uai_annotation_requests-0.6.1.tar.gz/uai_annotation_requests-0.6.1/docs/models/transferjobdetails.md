# TransferJobDetails

Details about the transfer job
that copied data into UAI storage.

The counters object contains detailed
information about objects found in source,
objects copied, skipped and bytes transferred.


## Fields

| Field                                                 | Type                                                  | Required                                              | Description                                           |
| ----------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------- |
| `counters`                                            | Dict[str, *str*]                                      | :heavy_minus_sign:                                    | Construct a type with a set of properties K of type T |
| `end_time`                                            | *str*                                                 | :heavy_check_mark:                                    | N/A                                                   |
| `start_time`                                          | *str*                                                 | :heavy_check_mark:                                    | N/A                                                   |
| `status`                                              | [models.Status](../models/status.md)                  | :heavy_check_mark:                                    | N/A                                                   |