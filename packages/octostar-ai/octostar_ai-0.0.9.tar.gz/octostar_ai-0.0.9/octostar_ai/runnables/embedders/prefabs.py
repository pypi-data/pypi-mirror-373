from typing import Optional
from octostar_ai.utils.gpu import get_device
import logging

logger = logging.getLogger(__name__)

def default_rag_embedder(openai_api_key: Optional[str] = None, model: Optional[str] = None, device: Optional[str] = None):
    """Get the default embedder for Retrieval-Augmented Generation (RAG)."""
    if openai_api_key:
        from octostar_ai.runnables.embedders.commons import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=model or "text-embedding-3-small", model_version="1", api_key=openai_api_key
        )

    from octostar_ai.runnables.embedders.commons import HuggingFaceEmbeddings

    model_name = model or "sentence-transformers/all-mpnet-base-v2"
    model_kwargs = {"device": device or get_device()}
    encode_kwargs = {"normalize_embeddings": False}
    try:
        return HuggingFaceEmbeddings(
            model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
        )
    except Exception as e:
        logger.warning(f"Failed to load model on device {model_kwargs['device']}: {e}")
        if model_kwargs["device"] != "cpu":
            model_kwargs["device"] = "cpu"
            return HuggingFaceEmbeddings(
                model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
            )
        else:
            raise e
