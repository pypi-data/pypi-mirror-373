from typing import Literal

from dashscope import TextEmbedding

from .base import (
    BaseEmbeddings,
    DenseOutput,
    HybridOutput,
    RetrievalMode,
    SparseOutput,
)


class QwenEmbeddings(BaseEmbeddings):
    def __init__(self, *, model: str = "text-embedding-v4", dimensions: int = 1024):
        super().__init__(model=model, dimensions=dimensions)

    def _embed_texts(
        self,
        texts: list[str],
        text_type: Literal["document", "query"],
        retrieval_mode: RetrievalMode = RetrievalMode.DENSE,
    ) -> DenseOutput | SparseOutput | HybridOutput:
        response = TextEmbedding.call(
            model=self.model,
            input=texts,
            text_type=text_type,
            output_type="dense&sparse"
            if retrieval_mode == RetrievalMode.HYBRID
            else retrieval_mode,
        )
        if response.status_code != 200:
            raise Exception(
                f"Failed to embed documents: {response.code} - {response.message}"
            )

        embeddings = response.output["embeddings"]
        dense_output: DenseOutput = [
            embedding["embedding"]
            for embedding in embeddings
            if embedding.get("embedding")
        ]

        sparse_output: SparseOutput = [
            (
                [item["index"] for item in embedding["sparse_embedding"]],
                [item["value"] for item in embedding["sparse_embedding"]],
            )
            for embedding in embeddings
            if embedding.get("sparse_embedding")
        ]

        if retrieval_mode == RetrievalMode.DENSE:
            return dense_output
        elif retrieval_mode == RetrievalMode.SPARSE:
            return sparse_output
        elif retrieval_mode == RetrievalMode.HYBRID:
            return (dense_output, sparse_output)
