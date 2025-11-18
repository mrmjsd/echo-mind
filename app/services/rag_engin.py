import os
from langchain.schema import Document
from transformers import AutoTokenizer
from core.doc_parser import extract_text, get_available_files
from services.embedding_service import EmbeddingService
from services.vector_store_service import VectorStoreService
from core.config import MODELS_DIR, DEFAULT_HF_MODEL_ID
from services.llm_service import GroqClient
from core.logging_config import get_logger

logger = get_logger(__name__)

class RAGChatbot:
    def __init__(self, model_path=MODELS_DIR, max_tokens=500):
        self.model_path = model_path
        self.max_tokens = max_tokens

        # Determine effective model source: local directory if valid, else default HF model ID
        effective_model = self._resolve_model_source(self.model_path)
        logger.info("Initializing RAGChatbot with model source: %s", effective_model)

        # Initialize tokenizer and embedding service
        self.tokenizer = AutoTokenizer.from_pretrained(effective_model)
        self.embedding_service = EmbeddingService(effective_model)
        self.vectorstore_service = VectorStoreService(self.embedding_service)
        self.llm = GroqClient()  # <- Initialize Groq client
        self.load_documents()

    def load_documents(self):
        logger.info("Checking for existing index...")
        self.vectorstore_service.load_index()

        if self.vectorstore_service.documents:
            return  # Skip indexing again if already loaded

        logger.info("Indexing documents...")
        filenames = get_available_files()
        if not filenames:
            logger.warning("No valid documents found in docs directory.")
            return

        all_docs = []
        for filename in filenames:
            try:
                docs = extract_text(filename)
                all_docs.extend(docs)
            except Exception as e:
                logger.exception("Error processing document during indexing: %s", filename)

        if all_docs:
            self.vectorstore_service.add_documents(all_docs)
            logger.info("Indexed %d chunks.", len(all_docs))
        else:
            logger.warning("No content extracted from available documents.")

    def clear_data(self):
        self.vectorstore_service.clear_index()
        return True

    def answer(self, query: str, k: int = 5) -> str:
        results = self.vectorstore_service.similarity_search(query, k)
        if not results:
            return "No relevant information found."

        top_response = results[0].page_content.strip()
        tokens = self.tokenizer.tokenize(top_response)

        if len(tokens) > self.max_tokens:
            tokens = tokens[:self.max_tokens]
            top_response = self.tokenizer.convert_tokens_to_string(tokens)

        return top_response

    def llmanswer(self, query: str, k: int = 5) -> str:
        results = self.vectorstore_service.similarity_search(query, k)
        logger.debug("Top-%d retrieved documents: %s", k, [len(r.page_content) for r in results])
        if not results:
            return "No relevant information found."

        # Combine top-k chunks into a single context string
        context = "\n\n".join([doc.page_content.strip() for doc in results])

        # Generate response using Groq LLaMA
        try:
            response = self.llm.generate_answer(context, query)
            return response
        except Exception:
            logger.exception("LLM generation failed")
            return "An error occurred while generating the answer."

    def _resolve_model_source(self, local_path: str) -> str:
        """Return a valid model source for Transformers and SentenceTransformers.

        If a non-empty local directory is provided, use it. Otherwise, fall back to
        DEFAULT_HF_MODEL_ID (can be overridden via HF_MODEL_ID env).
        """
        try:
            if isinstance(local_path, str) and os.path.isdir(local_path):
                # Check if directory has any files (basic sanity check)
                entries = [f for f in os.listdir(local_path) if not f.startswith('.')]
                if entries:
                    return local_path
                logger.warning("Local model directory '%s' is empty; using default HF model '%s'", local_path, DEFAULT_HF_MODEL_ID)
            else:
                logger.warning("Local model path '%s' not found; using default HF model '%s'", local_path, DEFAULT_HF_MODEL_ID)
        except Exception:
            logger.exception("Error while inspecting local model path '%s'", local_path)

        return DEFAULT_HF_MODEL_ID
