from uuid import uuid4

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from sparkden.models.knowledge import DataChunk, ParseResult, ParseResultType

from .base import BaseDataSplitter


class DefaultSplitter(BaseDataSplitter):
    async def split(self, data: ParseResult) -> list[DataChunk]:
        if data.data_type == ParseResultType.MARKDOWN:
            assert isinstance(data.data, str)
            return self._split_markdown(data.data)
        elif data.data_type == ParseResultType.TEXT:
            assert isinstance(data.data, str)
            return self._split_text(data.data)
        else:
            raise ValueError(f"Unsupported data type: {data.data_type}")

    def _split_markdown(self, markdown: str) -> list[DataChunk]:
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header1"),
                ("##", "Header2"),
                ("###", "Header3"),
                ("####", "Header4"),
                ("#####", "Header5"),
                ("######", "Header6"),
            ],
        )
        chunks = markdown_splitter.split_text(markdown)
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = recursive_splitter.split_documents(chunks)
        return [
            DataChunk(
                id=str(uuid4().hex),
                content=chunk.page_content,
                metadata=chunk.metadata,
            )
            for chunk in chunks
        ]

    def _split_text(self, text: str) -> list[DataChunk]:
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

        chunks = recursive_splitter.create_documents([text])

        return [
            DataChunk(
                id=str(uuid4().hex),
                content=chunk.page_content,
                metadata=chunk.metadata,
            )
            for chunk in chunks
        ]
