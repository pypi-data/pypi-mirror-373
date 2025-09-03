from typing import Any, Dict, Optional, Union, List
from langchain_core.documents import Document
import json
import builtins
import io


class JsonDocument(Document):
    json_content: Dict[str, Any]

    def __init__(
        self,
        json_content: Union[Dict[str, Any], Any],
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        A document class designed for JSON data.

        Args:
            json_content (Union[Dict[str, Any], Any]): A valid JSON dictionary.
                If another type of data is provided, it will be converted best-effort.
            metadata (Optional[Dict[str, Any]]): Metadata associated with the binary document.
        """
        if not isinstance(json_content, dict):
            try:
                json_content = json.loads(json_content)
            except:
                json_content = {"content": json_content}
        json_content = JsonDocument._safe_convert_json_keys(json_content)
        json_content = json.loads(
            json.dumps(json_content, default=TextDocument.safe_convert_to_string)
        )
        super().__init__(
            page_content="",
            json_content=json_content,
            metadata=metadata or {},
            **kwargs,
        )

    def __str__(self) -> str:
        if self.metadata:
            return f"json_content='{self.json_content}' metadata={self.metadata}"
        else:
            return f"json_content='{self.json_content}'"

    def _safe_convert_json_keys(source: dict) -> dict:
        for key, value in source.items():
            if not isinstance(key, str):
                source[str(key)] = source.pop(key)
                key = str(key)
            if isinstance(value, dict):
                source[key] = JsonDocument._safe_convert_json_keys(value)
        return source


class TextDocument(Document):
    def __init__(
        self,
        page_content: Union[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        A document class designed for JSON data.

        Args:
            page_content (Dict[str, Any]): The text contents. If not a string, it will be converted best-effort.
            metadata (Optional[Dict[str, Any]]): Metadata associated with the binary document.
        """
        page_content = TextDocument.safe_convert_to_string(page_content)
        super().__init__(page_content=page_content, metadata=metadata or {}, **kwargs)

    @staticmethod
    def safe_convert_to_string(value: Any, skip_default: bool = False) -> Any:
        match type(value):
            case builtins.bytes:
                return value.decode("utf-8", errors="ignore")
            case _:
                if not skip_default:
                    return str(value)
        return value


class BinaryDocument(Document):
    binary_content: bytes

    def __init__(
        self,
        binary_content: Union[bytes, Any],
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        A document class designed for binary data.

        Args:
            binary_content (bytes): The binary content of the document (e.g., an image, audio, or file content).
                If not bytes, the data will be converted best-effort.
            metadata (Optional[Dict[str, Any]]): Metadata associated with the binary document.
        """
        binary_content = BinaryDocument.safe_convert_to_bytes(binary_content, True)
        if not isinstance(binary_content, bytes):
            binary_content = BinaryDocument.safe_convert_to_bytes(
                TextDocument.safe_convert_to_string(binary_content)
            )
        super().__init__(
            page_content="",
            binary_content=binary_content,
            metadata=metadata or {},
            **kwargs,
        )

    def __str__(self) -> str:
        if self.metadata:
            return f"binary_content='{self.binary_content}' metadata={self.metadata}"
        else:
            return f"binary_content='{self.binary_content}'"

    @staticmethod
    def safe_convert_to_bytes(
        value: Any, skip_default: bool = False
    ) -> Union[bytes, Any]:
        if not isinstance(value, bytes):
            match type(value):
                case builtins.bytearray | builtins.memoryview:
                    value = bytes(value)
                case io.BytesIO:
                    value = value.getvalue()
                case io.FileIO:
                    value = value.read()
                case builtins.int | builtins.float:
                    value = value.tobytes()
                case _:
                    if not skip_default:
                        value = bytes(str(value), encoding="utf-8")
        return value


class VectorizedDocument(Document):
    vector_data: List[float]
    document: Document

    def __init__(self, vector_data: List[float], document: Document, **kwargs):
        """
        A wrapper around a Document, containing the embedded data for the document.

        Args:
            vector_data (List[float]): The vector associated with the Document.
            document (Document): The original document.
        """
        super().__init__(
            page_content="", vector_data=vector_data, document=document, **kwargs
        )

    @property
    def vector_dim(self):
        return len(self.vector_data)

    def __str__(self) -> str:
        return self.document.__str__() + f" (VECTORIZED dim={self.vector_dim})"
