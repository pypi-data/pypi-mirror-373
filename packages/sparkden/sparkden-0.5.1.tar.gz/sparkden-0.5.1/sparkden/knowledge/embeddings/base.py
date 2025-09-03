from abc import ABC, abstractmethod
from typing import Literal, cast, overload

from sparkden.models.knowledge import RetrievalMode

DenseVector = list[float]
SparseVector = tuple[list[int], list[float]]
HybridVector = tuple[DenseVector, SparseVector]
DenseOutput = list[DenseVector]
SparseOutput = list[SparseVector]
HybridOutput = tuple[DenseOutput, SparseOutput]
TextType = Literal["document", "query"]

EmbeddingsOutput = DenseOutput | SparseOutput | HybridOutput
SingleEmbeddingOutput = DenseVector | SparseVector | HybridVector


class BaseEmbeddings(ABC):
    def __init__(
        self,
        *,
        model: str,
        dimensions: int,
    ):
        self.model = model
        self.dimensions = dimensions

    @overload
    def embed_documents(
        self,
        texts: list[str],
        retrieval_mode: Literal[RetrievalMode.DENSE],
    ) -> DenseOutput: ...
    @overload
    def embed_documents(
        self,
        texts: list[str],
        retrieval_mode: Literal[RetrievalMode.SPARSE],
    ) -> SparseOutput: ...
    @overload
    def embed_documents(
        self,
        texts: list[str],
        retrieval_mode: Literal[RetrievalMode.HYBRID],
    ) -> HybridOutput: ...

    def embed_documents(
        self,
        texts: list[str],
        retrieval_mode: RetrievalMode = RetrievalMode.DENSE,
    ) -> EmbeddingsOutput:
        return self._embed_texts(texts, "document", retrieval_mode)

    @overload
    def embed_query(
        self, text: str, retrieval_mode: Literal[RetrievalMode.DENSE]
    ) -> DenseVector: ...
    @overload
    def embed_query(
        self, text: str, retrieval_mode: Literal[RetrievalMode.SPARSE]
    ) -> SparseVector: ...
    @overload
    def embed_query(
        self, text: str, retrieval_mode: Literal[RetrievalMode.HYBRID]
    ) -> HybridVector: ...

    def embed_query(
        self,
        text: str,
        retrieval_mode: RetrievalMode = RetrievalMode.DENSE,
    ) -> SingleEmbeddingOutput:
        return self._embed_text(text, "query", retrieval_mode)

    def _embed_text(
        self, text: str, text_type: TextType, retrieval_mode: RetrievalMode
    ) -> SingleEmbeddingOutput:
        if retrieval_mode == RetrievalMode.DENSE:
            vectors = cast(
                DenseOutput, self._embed_texts([text], text_type, RetrievalMode.DENSE)
            )
            return vectors[0]
        elif retrieval_mode == RetrievalMode.SPARSE:
            sparse_vectors = cast(
                SparseOutput, self._embed_texts([text], text_type, RetrievalMode.SPARSE)
            )
            return sparse_vectors[0]
        elif retrieval_mode == RetrievalMode.HYBRID:
            vectors, sparse_vectors = cast(
                HybridOutput, self._embed_texts([text], text_type, RetrievalMode.HYBRID)
            )
            return vectors[0], sparse_vectors[0]
        else:
            raise ValueError(f"Invalid retrieval mode: {retrieval_mode}")

    @abstractmethod
    def _embed_texts(
        self,
        texts: list[str],
        text_type: TextType,
        retrieval_mode: RetrievalMode = RetrievalMode.DENSE,
    ) -> DenseOutput | SparseOutput | HybridOutput:
        pass
