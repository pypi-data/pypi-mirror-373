from .qwen import QwenEmbeddings

# TODO: determine which embeddings to use by app config
Embeddings = QwenEmbeddings

__all__ = ["Embeddings"]
