from langchain_text_splitters.json import RecursiveJsonSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import re
from collections import Counter
from ..documents.commons import JsonDocument, TextDocument, Document
from ..documents.entities import OSEntityDocument
from .commons import MapSplitter, JsonSplitter, ChainedSplitter
from .entities import OSEntitySplitter
from .postprocessors.commons import ReEnumeratePostProcessor


def default_entity_splitter():
    """
    Get the default entity splitter for an entity (OSEntityDocument).
    The splitter takes care of chunking the entity record, metadata, relationships, and so on.
    """

    def _none_map(doc: Document, **kwargs) -> TextDocument:
        return TextDocument(page_content="", metadata=doc.metadata)

    def _tags_map(doc: JsonDocument, **kwargs) -> TextDocument:
        json_content = doc.json_content
        tags = []
        for elem in json_content["content"]:
            if elem.get("label"):
                tags.append(str(elem.get("label")))
        tags = Counter(tags)
        tags_text = "Image tags: " + ", ".join(
            f"{item} ({count})" for item, count in tags.items()
        )
        return TextDocument(page_content=tags_text, metadata=doc.metadata)

    # Chunkers for specific fields. For linkcharts, we filter out unnecessary fields
    linkchart_keep_base_fields = [
        r"nodes\[\d+\]._entityData",
        r"edges\[\d+\]._edgeData",
    ]
    linkchart_keep_relationship_fields = [
        r"relationship_name",
        r"inverse_name",
        r"description",
    ]
    special_splitters = {
        "annotations.extract:txt": (
            TextDocument,
            ChainedSplitter(
                RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""]),
                ReEnumeratePostProcessor("chunk_id"),
            ),
        ),
        "annotations.image:annotations": (JsonDocument, MapSplitter(_tags_map)),
        "annotations.extract:metadata": (
            JsonDocument,
            OSEntitySplitter.get_splitter_json_to_text(),
        ),
        "record.os_item_content": (JsonDocument, None),
        "record.os_item_content.data": (
            JsonDocument,
            OSEntitySplitter.get_splitter_json_to_text(
                ignore_fields=[
                    re.compile(r".*#relationships_fetched"),
                    re.compile(
                        r"edges\[\d+\]._edgeData.relationship.(?!("
                        + "|".join(linkchart_keep_relationship_fields)
                        + r")).*"
                    ),
                    re.compile(
                        r"^(?!(" + "|".join(linkchart_keep_base_fields) + r")).*"
                    ),
                ]
            ),
        ),
        "record.metadata": (JsonDocument, OSEntitySplitter.get_splitter_json_to_text()),
    }

    # Chunker for the first chunk (no-op)
    base_splitters = MapSplitter(_none_map)

    # Chunkers for the record fields. Notice we ignore the fields treated specially above
    record_splitters = ChainedSplitter(
        OSEntitySplitter.get_splitter_json_to_text(
            ignore_fields=[
                k[7:] for k in special_splitters.keys() if k.startswith("record.")
            ]
        ),
        ReEnumeratePostProcessor("chunk_id"),
    )

    # Chunkers for the entity's relationships. They are also json objects, so it's more of the same. We only keep
    # the relationship label and a few other fields.
    relationship_keep_fields = [
        r"relationship\.(entity_label|entity_type|os_workspace|os_entity_uid|os_entity_uid_from|os_entity_uid_to|os_relationship_name)",
        r"other_entity\.(entity_label|entity_type|os_workspace|os_entity_uid)",
        r"direction",
    ]
    relationship_splitters = ChainedSplitter(
        MapSplitter(OSEntitySplitter.parse_relationship_as_text),
        OSEntitySplitter.get_splitter_json_to_text(
            ignore_fields=[
                re.compile(r"^(?!(" + "|".join(relationship_keep_fields) + r")).*")
            ]
        ),
        ## TODO: Add a recombinator to merge relationships from the same workspace
        ReEnumeratePostProcessor("chunk_id", "os_workspace"),
    )

    # Chunkers for the entity's attachment (if any). For now we don't use it.
    attachment_splitters = None

    # Chunkers for the entity's AI annotations. We don't use it since we'd rather use the special splitters for each field.
    annotations_splitter = None

    return OSEntitySplitter(
        base_splitters,
        record_splitters,
        relationship_splitters,
        attachment_splitters,
        annotations_splitter,
        special_splitters,
    )


def default_json_splitter():
    """
    Get the default json splitter for a JSON-compatible input (JSONDocument).
    """
    return ChainedSplitter(
        JsonSplitter(RecursiveJsonSplitter(), as_text=True),
        RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""]),
    )


def default_text_splitter():
    """
    Get the default text splitter for a string input (TextDocument).
    """
    return RecursiveCharacterTextSplitter(separators=["\n\n", "\n", " ", ""])
