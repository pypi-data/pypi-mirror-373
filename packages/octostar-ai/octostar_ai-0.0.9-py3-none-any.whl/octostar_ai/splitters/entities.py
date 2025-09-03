from typing import Optional, Dict, Tuple, Type, Sequence, Any
from warnings import warn
from langchain_core.documents import Document
from ..documents.commons import JsonDocument, TextDocument
from ..documents.entities import OSEntityDocument
from .postprocessors.commons import TrimEmptyPostProcessor, ReEnumeratePostProcessor
from .commons import Splitter, JsonSplitter, ChainedSplitter
from langchain_text_splitters.json import RecursiveJsonSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from typing import List, Union


class OSEntitySplitter(Splitter):
    """Interface for splitting Octostar entities into chunks."""

    def __init__(
        self,
        base_splitter: Splitter,
        record_splitter: Optional[Splitter],
        relationship_splitter: Optional[Splitter],
        attachment_splitter: Optional[Splitter],
        annotations_splitter: Optional[Splitter],
        special_splitters: Optional[
            Dict[
                str,
                Tuple[
                    Type[Document],
                    Splitter,
                ],
            ]
        ],
    ):
        """Create a new OSEntitySplitter.

        Args:
            base_splitter: A JSON splitter which should produce the most important chunk to identify the entity
            record_splitter: A JSON splitter which will be used for the entity record
            relationship_splitter: A JSON splitter which will be used for the entity relationships records
            attachment_splitter: A binary splitter to convert binary contents into a sequence of Document
            annotations_splitter: A JSON splitter which will be used for the entity's pipeline annotations
            special_splitters: A mapping from field names to splitters, for record fields that should be handled differently.
                Nested fields can be accessed with the "." notation.
                Preface the field name with either "record", "relationships", "attachment" or "annotations".
        """
        self.base_splitter = base_splitter
        self.record_splitter = record_splitter
        self.relationship_splitter = relationship_splitter
        self.attachment_splitter = attachment_splitter
        self.annotations_splitter = annotations_splitter
        self.special_splitters = special_splitters or {}

    def _transform_entity(self, entity: OSEntityDocument):
        all_chunks = []
        assert self.base_splitter
        base_docs = [JsonDocument(entity.record, metadata={"type": "base"})]
        base_docs = self.base_splitter.transform_documents(base_docs, entity=entity)
        if len(base_docs) > 1:
            warn(f"Base chunk is of length {len(base_docs)}, expected 1!")
        assert bool(base_docs)
        all_chunks.append(base_docs[0])
        if self.record_splitter:
            record_docs = [JsonDocument(entity.record, metadata={"type": "record"})]
            record_docs = self.record_splitter.transform_documents(
                record_docs, entity=entity
            )
            all_chunks.extend(record_docs)
        if self.annotations_splitter:
            annotations_docs = [
                JsonDocument(entity.annotations, metadata={"type": "annotation"})
            ]
            annotations_docs = self.annotations_splitter.transform_documents(
                record_docs, entity=entity
            )
            all_chunks.extend(annotations_docs)
        if self.relationship_splitter:
            rel_docs = [
                JsonDocument(
                    {"relationship": rel[0], "other_entity": rel[1]},
                    metadata={
                        "type": "relationship",
                        "os_workspace": rel[1].get("os_worspace"),
                        "os_relationship_workspace": rel[0].get("os_workspace"),
                    },
                )
                for rel in entity.relationships
            ]
            rel_docs = self.relationship_splitter.transform_documents(
                rel_docs, entity=entity
            )
            all_chunks.extend(rel_docs)
        all_special_docs = []
        for field_name, (doc_cls, splitter) in self.special_splitters.items():
            if splitter:
                field_base_key, field_name = field_name.split(".", 1)
                field = getattr(entity, field_base_key)
                is_field_valid = True
                for field_key in field_name.split("."):
                    try:
                        if isinstance(field, dict):
                            field = field[field_key]
                        elif isinstance(field, list):
                            field = field[int(field_key)]
                        else:
                            raise KeyError(field_key)
                    except KeyError:
                        is_field_valid = False
                        break
                if not is_field_valid:
                    continue
                special_docs = [
                    doc_cls(
                        field,
                        metadata={
                            "type": "other",
                            "field_name": field_base_key + "." + field_name,
                        },
                    )
                ]
                special_docs = splitter.transform_documents(special_docs, entity=entity)
                all_special_docs.extend(special_docs)
        all_chunks.extend(all_special_docs)
        all_chunks = TrimEmptyPostProcessor().transform_documents(all_chunks)
        return all_chunks

    def transform_documents(
        self, documents: Sequence[OSEntityDocument], **kwargs: Any
    ) -> Sequence[TextDocument]:
        """Transform a list of documents.

        Args:
            documents: A sequence of Octostar entities to be transformed.

        Returns:
            A sequence of flat Documents (text + metadata).
        """
        entities = documents
        all_chunks = []
        for entity in entities:
            all_chunks.extend(self._transform_entity(entity))
        return all_chunks

    @staticmethod
    def prepend_base_entity_info(doc: Document, entity: OSEntityDocument):
        ## TODO: add some more fields for files
        base_doc = f"{entity.record['entity_label']} ({entity.record['entity_type']}) contained in Workspace {entity.record['os_workspace']}"
        doc.page_content = base_doc + "\n" + doc.page_content
        doc.page_content = doc.page_content.strip()
        return doc

    @staticmethod
    def get_splitter_json_to_text(
        ignore_fields: List[Union[str, re.Pattern]] = [],
        separators: List[str] = ["\n\n", "\n", " ", ""],
        re_enumerate_on: str = "chunk_id",
    ):
        return ChainedSplitter(
            JsonSplitter(
                RecursiveJsonSplitter(), as_text=True, ignore_fields=ignore_fields
            ),
            RecursiveCharacterTextSplitter(separators=separators),
            ReEnumeratePostProcessor(index_name=re_enumerate_on),
        )

    @staticmethod
    def parse_relationship_as_text(rel: JsonDocument, entity: OSEntityDocument):
        contents = rel.json_content
        direction = None
        if (
            contents["relationship"]["os_entity_uid_from"]
            == contents["relationship"]["os_entity_uid_from"]
        ):
            direction = 0
        elif (
            contents["relationship"]["os_entity_uid_to"]
            == contents["other_entity"]["os_entity_uid"]
        ):
            direction = 1
        elif (
            contents["relationship"]["os_entity_uid_from"]
            == contents["other_entity"]["os_entity_uid"]
        ):
            direction = -1
        if not direction:
            direction = 0
        this_entity_txt = (
            f"{entity.record['entity_label']} ({entity.record['os_entity_uid']})"
        )
        other_entity_txt = f"{contents['other_entity']['entity_label']} ({contents['other_entity']['os_entity_uid']})"
        relationship_txt = contents["relationship"]["os_relationship_name"].replace(
            "_", " "
        )
        text = ""
        match direction:
            case 1:
                text = f"{this_entity_txt} {relationship_txt} {other_entity_txt}"
            case -1:
                text = f"{other_entity_txt} {relationship_txt} {this_entity_txt}"
            case 0:
                text = f"{relationship_txt} between {this_entity_txt} and {other_entity_txt}"
        contents["direction"] = text
        return rel
