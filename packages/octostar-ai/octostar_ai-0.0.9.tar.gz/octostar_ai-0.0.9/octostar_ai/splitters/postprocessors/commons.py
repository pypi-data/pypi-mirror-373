from abc import ABC
from collections.abc import Sequence
from typing import Any, List, Optional, Callable
from langchain_core.documents import Document

from ..commons import Splitter
from ...documents.commons import TextDocument


class SplitterPostProcessor(Splitter, ABC):
    """Unified interface for post-processing chunks (e.g. recombination, re-enumerate)."""

    pass


class ReEnumeratePostProcessor(SplitterPostProcessor):
    """Post-Processor that sets a metadata field as an increasing integer, useful to track chunk sequentiality."""

    def __init__(self, index_name: str, reset_fields: Optional[List[str]] = None):
        """
        Args:
            index_name (str): The name of the metadata field to modify.
            reset_fields (Optional[List[str]], optional): The name of the fields on which to reset the counting to 0.
                Defaults to None.
        """
        self.index_name = index_name
        self.reset_fields = reset_fields or []

    def transform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> Sequence[Document]:
        curr_index = 0
        curr_fields = tuple()
        for doc in documents:
            doc_fields = tuple(doc.metadata.get(field) for field in self.reset_fields)
            if doc_fields != curr_fields:
                curr_index = 0
            doc.metadata[self.index_name] = curr_index
            curr_index += 1
        return documents


class TrimEmptyPostProcessor(SplitterPostProcessor):
    """Post-Processor that filters out any document with empty text contents."""

    def __init__(self, ignore_chars: Optional[List[str]] = None):
        """

        Args:
            ignore_chars (Optional[List[str]], optional): Characters to consider as whitespace for the trimming. Defaults to None.
        """
        self.ignore_chars = ignore_chars

    def transform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> Sequence[Document]:
        trimmed_documents = []
        for doc in documents:
            doc.page_content.strip(self.ignore_chars)
            if doc.page_content:
                trimmed_documents.append(doc)
        return trimmed_documents


class ReCombinePostProcessor(SplitterPostProcessor):
    def __init__(
        self,
        count_fn: Callable[[str], int],
        agg_metadata_fn: Callable[[dict, dict], dict],
        min_size: int,
        max_size: int,
        reset_fields: Optional[List[str]] = None,
    ):
        self.count_fn = count_fn
        self.agg_metadata_fn = agg_metadata_fn
        self.min_size = min_size
        self.max_size = max_size
        self.reset_fields = reset_fields or []

    def transform_documents(
        self, documents: Sequence[TextDocument], **kwargs: Any
    ) -> Sequence[TextDocument]:
        raise NotImplementedError()
