from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from pathlib import Path
from core.logging_config import get_logger

logger = get_logger(__name__)

def load_documents(file_path: str):
    ext = Path(file_path).suffix.lower()
    logger.debug("Loading documents from %s with extension %s", file_path, ext)
    if ext == ".pdf":
        return PyPDFLoader(file_path).load()
    elif ext == ".txt":
        return TextLoader(file_path).load()
    elif ext == ".docx":
        return Docx2txtLoader(file_path).load()
    else:
        logger.error("Unsupported file format for %s", file_path)
        raise ValueError("Unsupported file format")
