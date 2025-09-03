import os
from io import BytesIO

from minio import Minio, S3Error

from sparkden.models.knowledge import FileObject

from .utils import getenv

_minio_client: Minio | None = None


def get_minio_client() -> Minio:
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            endpoint=getenv("MINIO_ENDPOINT"),
            access_key=getenv("MINIO_ROOT_USER"),
            secret_key=getenv("MINIO_ROOT_PASSWORD"),
            secure=getenv("MINIO_SECURE", "false").lower() == "true",
            region=os.getenv("MINIO_REGION"),
        )
    return _minio_client


def object_exists(bucket_name: str, object_name: str) -> bool:
    try:
        minio_client = get_minio_client()
        minio_client.stat_object(bucket_name, object_name)
        return True
    except S3Error as e:
        if e.code == "NoSuchKey":
            return False
        raise e


def save_objects(bucket_name: str, objects: list[FileObject]) -> None:
    minio_client = get_minio_client()
    for object in objects:
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object.name,
            data=BytesIO(object.content),
            length=len(object.content),
            content_type=object.content_type,
        )


def get_object(bucket_name: str, object_name: str) -> FileObject | None:
    response = None
    try:
        minio_client = get_minio_client()
        response = minio_client.get_object(bucket_name, object_name)
        content_type = response.headers["content-type"]
        file = FileObject(
            name=object_name,
            content=response.data,
            content_type=content_type,
        )
    except S3Error as e:
        if e.code == "NoSuchKey":
            return None
        raise e
    finally:
        if response:
            response.close()
            response.release_conn()

    return file


def delete_objects(bucket_name: str, object_names: list[str]) -> None:
    minio_client = get_minio_client()
    for object_name in object_names:
        minio_client.remove_object(
            bucket_name=bucket_name,
            object_name=object_name,
        )
