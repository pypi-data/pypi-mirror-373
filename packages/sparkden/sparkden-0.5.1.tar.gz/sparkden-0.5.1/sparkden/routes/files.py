from datetime import timedelta
from os.path import basename

from litestar import Controller, get
from litestar.exceptions import NotFoundException
from litestar.response import Redirect
from sparkden.shared.minio import get_minio_client, object_exists


class FilesController(Controller):
    @get("/images/{bucket_name:str}/{object_name:path}")
    async def images(
        self, bucket_name: str, object_name: str, download: bool = False
    ) -> Redirect:
        if not object_exists(bucket_name, object_name):
            raise NotFoundException(
                f"File not found: bucket={bucket_name}, object_name={object_name}"
            )

        minio_client = get_minio_client()
        disposition_type = "attachment" if download else "inline"
        disposition = f'{disposition_type}; filename="{basename(object_name)}"'
        presigned_url = minio_client.presigned_get_object(
            bucket_name,
            object_name,
            expires=timedelta(seconds=60),
            response_headers={
                "response-content-disposition": disposition,
            },
        )

        return Redirect(
            path=presigned_url,
            status_code=303,
        )
