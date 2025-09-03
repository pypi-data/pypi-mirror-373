from langchain_openai import OpenAIEmbeddings as _OpenAIEmbeddings
from typing import Any, ClassVar


try:
    from langchain_huggingface import HuggingFaceEmbeddings as _HuggingFaceEmbeddings

    class HuggingFaceEmbeddings(_HuggingFaceEmbeddings):
        model_version: str

        def __init__(self, **kwargs: Any):
            """Initialize the sentence_transformer."""
            kwargs.setdefault("model_version", "1")
            super().__init__(**kwargs)

        def get_embedding_dimension(self) -> int:
            return self._client.get_sentence_embedding_dimension()

except ImportError:

    class MissingHuggingFaceEmbeddings:
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "HuggingFaceEmbeddings requires 'langchain_huggingface' to be installed. "
                "Install it using: pip install octostar-ai[gpu]"
            )

    HuggingFaceEmbeddings = MissingHuggingFaceEmbeddings


class OpenAIEmbeddings(_OpenAIEmbeddings):
    # Define static variables as class variables
    DEFAULT_MODEL: ClassVar[str] = "text-embedding-3-small"
    DEFAULT_DIMENSIONS: ClassVar[int] = 1536

    model_version: str
    model_name: str

    def __init__(self, **kwargs: Any):
        if not kwargs:
            kwargs = {}
        kwargs.setdefault("model_version", "1")
        kwargs.setdefault("model", self.DEFAULT_MODEL)
        kwargs.setdefault("model_name", self.DEFAULT_MODEL)
        kwargs.setdefault("dimensions", self.DEFAULT_DIMENSIONS)

        super().__init__(**kwargs)

    def get_embedding_dimension(self) -> int:
        return self.dimensions
