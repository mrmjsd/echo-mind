import os

# Absolute path to the project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Standardized reusable paths
MODELS_DIR = os.path.join(PROJECT_ROOT, "models", "model")
DOCS_DIR = os.path.join(PROJECT_ROOT, "data", "docs")
INDEX_PATH = os.path.join(PROJECT_ROOT, "vector_store.pkl")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")

# Default Hugging Face model to use when a local model directory is not present or invalid
# Can be overridden with HF_MODEL_ID environment variable
DEFAULT_HF_MODEL_ID = os.getenv("HF_MODEL_ID", "sentence-transformers/all-MiniLM-L6-v2")
