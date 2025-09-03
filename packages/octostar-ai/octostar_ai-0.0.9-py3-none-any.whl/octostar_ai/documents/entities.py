from typing import Any, List, Dict, Tuple, Literal, Optional
from langchain_core.documents import Document


class OSEntityDocument(Document):
    type: Literal["OSEntityDocument"] = "OSEntityDocument"
    record: Dict[str, Any]
    relationships: List[Tuple[Dict[str, Any], Dict[str, Any]]]
    annotations: Dict[str, Any]
    attachment: Optional[bytes] = None

    def __init__(
        self,
        record: Dict[str, Any],
        relationships: List[Tuple[Dict[str, Any], Dict[str, Any]]],
        annotations: Dict[str, Any],
        attachment: Optional[bytes] = None,
        **kwargs: Any,
    ):
        """
        A document class designed for an Octostar entity.

        Args:
            record (Dict[str, Any]): The entity record.
            relationships (List[Tuple[Dict[str, Any], Dict[str, Any]]]): A list of entity relationships, each expressed
                as a tuple (relationship_record, target_concept_record). Either of these two elements can be None.
            annotations (Dict[str, Any]): The entity's pipeline annotations.
            attachment: Optional[bytes]: The entity's attachment, if any.
        """
        super().__init__(
            record=record,
            relationships=relationships,
            annotations=annotations,
            attachment=attachment,
            page_content="",
            **kwargs,
        )

    def __str__(self) -> str:
        return (
            f"entity_type='{self.record['os_concept']}', "
            f"n_fields='{len([v for v in self.record.values() if v is not None])}"
            f"n_annotations={len([v for v in self.annotations.values() if v is not None])}"
            f"attachment_size={len(self.attachment) if self.attachment else 0}"
        )
