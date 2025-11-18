import numpy as np
import os
import pickle
from typing import List
from langchain.schema import Document
from core.config import INDEX_PATH
from core.logging_config import get_logger

logger = get_logger(__name__)

class VectorStoreService:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service
        self.vectors = []
        self.documents = []
        self.index_path = INDEX_PATH

    def add_documents(self, docs: List[Document]):
        logger.info("Adding %d documents to vector store", len(docs))
        texts = [doc.page_content for doc in docs]
        embeddings = self.embedding_service.embed(texts)
        self.vectors.extend(embeddings)
        self.documents.extend(docs)
        self.save_index()  # Save after adding

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        if not self.vectors:
            return []

        logger.debug("Performing similarity search for query with k=%d", k)
        query_vec = self.embedding_service.embed_single(query)
        similarities = np.dot(self.vectors, query_vec)
        top_k_indices = np.argsort(similarities)[-k:][::-1]
        return [self.documents[i] for i in top_k_indices]

    def save_index(self):
        data = {
            "vectors": self.vectors,
            "documents": self.documents
        }
        try:
            with open(self.index_path, "wb") as f:
                pickle.dump(data, f)
            logger.info("Vector index saved: %s", self.index_path)
        except Exception:
            logger.exception("Failed to save vector index to %s", self.index_path)

    def load_index(self):
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    self.vectors = data.get("vectors", [])
                    self.documents = data.get("documents", [])
                logger.info("Loaded %d documents from index.", len(self.documents))
            except Exception:
                logger.exception("Failed to load vector index from %s", self.index_path)
        else:
            logger.info("No existing index found.")

    def clear_index(self):
        self.vectors = []
        self.documents = []
        if os.path.exists(self.index_path):
            try:
                os.remove(self.index_path)
            except Exception:
                logger.warning("Failed to remove index file: %s", self.index_path)
        logger.info("Vector store cleared.")
