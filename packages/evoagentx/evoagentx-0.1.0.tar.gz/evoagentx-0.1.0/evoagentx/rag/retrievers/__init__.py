from typing import Optional

from llama_index.core.indices.base import BaseIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.graph_stores.types import GraphStore

from .base import BaseRetrieverWrapper, RetrieverType
from .vector_retriever import VectorRetriever
from .graph_retriever import GraphRetriever
from evoagentx.rag.schema import Query
from evoagentx.core.logging import logger
from evoagentx.models.base_model import BaseLLM
from evoagentx.storages.base import StorageHandler


__all__ = ['VectorRetriever', 'GraphRetriever', 'RetrieverFactory', 'BaseRetrieverWrapper']

class RetrieverFactory:
    """Factory for creating retrievers."""

    def create(
        self,
        retriever_type: str,
        llm: Optional[BaseLLM] = None,  # for graph build
        index: Optional[BaseIndex] = None,
        graph_store: Optional[GraphStore] = None,
        embed_model: Optional[BaseEmbedding] = None,
        query: Optional[Query] = None,    # Only for set topk
        storage_handler: Optional[StorageHandler] = None  # Only use in graph_retrieve
    ) -> BaseRetrieverWrapper:
        """Create a retriever based on configuration."""
        if retriever_type == RetrieverType.VECTOR.value:
            if not index:
                raise ValueError("Index required for vector retriever")
            retriever = VectorRetriever(index=index, top_k=query.top_k if query else 5)
        elif retriever_type == RetrieverType.GRAPH.value:
            if not (graph_store and embed_model and llm):
                raise ValueError("Graph store, embed model and llm model required for graph retriever")

            retriever = GraphRetriever(
                llm=llm,
                graph_store=graph_store,
                embed_model=embed_model,
                vector_store=storage_handler.vector_store,
                top_k=query.top_k if query else 5
            )
        else:
            raise ValueError(f"Unsupported retriever type: {retriever_type}")
        
        logger.info(f"Created retriever: {retriever_type}")
        return retriever