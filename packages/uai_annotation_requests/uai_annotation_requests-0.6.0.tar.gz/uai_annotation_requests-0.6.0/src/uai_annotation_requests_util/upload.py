import os
import shutil
import tempfile

import httpx

from uai_annotation_requests.models.annotationrequestdto import AnnotationRequestDTO
from uai_annotation_requests.models.clipdto import ClipDTO
from uai_annotation_requests.models.publicapidataintakestrategy import (
    PublicAPIDataIntakeStrategy,
)
from uai_annotation_requests_util.errors import (
    UaiNoUploadUrlError,
    UaiUnexpectedFileError,
    UaiUploadNotExpectedError,
)


def uai_upload_data(
    anno_request: AnnotationRequestDTO,
    clip: ClipDTO,
    path: str,
) -> None:
    """Uploads sensor data for a clip in an annotation request.
    The upload is only applicable for projects using the UPLOAD_GCS
    data intake strategy. The path should reference either a directory
    or a zip file containing the sensor data for the intended clip.

    Raises
    -------
    UaiUploadNotExpectedError
        if the data_intake_strategy for this project is not compatible with uai_upload_data

    UaiNoUploadUrlError
        if the clip is not accepting uploads at the moment, for example if processing has already begun

    UaiUnexpectedFileError
        if the referenced file or directory is not of supported types or doesn't exist


    """
    if anno_request.data_intake_strategy is not PublicAPIDataIntakeStrategy.UPLOAD_GCS:
        raise UaiUploadNotExpectedError(f"data_intake_strategy must be {PublicAPIDataIntakeStrategy.UPLOAD_GCS}")

    if clip.upload_url is None:
        raise UaiNoUploadUrlError("clip is not expecting an upload, missing upload_url")

    if os.path.isfile(path):
        if not path.endswith(".zip"):
            raise UaiUnexpectedFileError(f"unexpected file extension {path}, expected .zip")

        files = {"file": open(path, "rb")}
        httpx.request(method="PUT", url=clip.upload_url, files=files)
        return

    if os.path.isdir(path):
        with tempfile.TemporaryDirectory() as tempdir:
            shutil.make_archive(
                tempdir + "/data",
                "zip",
                path,
            )

            files = {"file": open(tempdir + "/data.zip", "rb")}
            httpx.request(method="PUT", url=clip.upload_url, files=files)
        return

    raise UaiUnexpectedFileError(f"path {path} must reference a directory or a zip file to upload")
