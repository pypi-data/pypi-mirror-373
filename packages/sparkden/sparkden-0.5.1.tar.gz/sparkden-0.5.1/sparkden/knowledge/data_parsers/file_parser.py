from typing import Any

import pymupdf
from sparkden.models.knowledge import (
    FileExtractConfig,
    FileObject,
    ParseResult,
    ParseResultType,
)
from sparkden.models.shared import BaseModel
from sparkden.shared.pymupdf_rag import to_markdown

from .base import BaseDataParser


class FileData(BaseModel):
    file: FileObject


class FileParser(BaseDataParser):
    def __init__(self):
        super().__init__(FileData)

    async def parse(
        self,
        input_data: dict[str, Any] | FileData,
        file_extract_config: FileExtractConfig,
    ) -> ParseResult:
        data = self._parse_input_data(input_data)

        if data.file.content_type == "text/plain":
            return self._parse_text_file(data.file, file_extract_config)
        elif data.file.content_type == "application/pdf":
            return self._parse_pdf_file(data.file, file_extract_config)
        else:
            raise ValueError(f"Unsupported file type: {data.file.content_type}")

    @staticmethod
    def _parse_text_file(
        file: FileObject, file_extract_config: FileExtractConfig
    ) -> ParseResult:
        return ParseResult(
            data=file.content.decode("utf-8"),
            data_type=ParseResultType.TEXT,
            extracted_files=[
                FileObject(
                    name=file_extract_config.parsed_object_name,
                    content=file.content,
                    content_type=file.content_type,
                ),
            ],
        )

    @staticmethod
    def _parse_pdf_file(
        file: FileObject, file_extract_config: FileExtractConfig
    ) -> ParseResult:
        doc = pymupdf.open(stream=file.content, filetype="pdf")
        extracted_images: list[FileObject] = []

        def extract_image(image_data: bytes, image_name: str) -> str:
            extracted_images.append(
                FileObject(
                    name=image_name,
                    content=image_data,
                    content_type="image/png",
                )
            )
            return f"/images/{file_extract_config.bucket_name}/{image_name}"

        markdown = to_markdown(
            doc,
            filename=file_extract_config.object_base_name,
            write_images=extract_image is not None,
            on_write_image=extract_image,
            image_format="png",
        )

        return ParseResult(
            data=markdown,
            data_type=ParseResultType.MARKDOWN,
            extracted_files=[
                FileObject(
                    name=file_extract_config.parsed_object_name,
                    content=markdown.encode("utf-8"),
                    content_type="text/markdown",
                ),
                *extracted_images,
            ],
        )
