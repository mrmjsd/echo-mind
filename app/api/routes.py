from fastapi import APIRouter, UploadFile, File, HTTPException
from services.chatbot.bot import RuleBasedBot
from services.rag_engin import RAGChatbot
from core.logging_config import get_logger
import shutil
import os
from core.config import DOCS_DIR
from services.translator import translate_to_english

# Setup logging
logger = get_logger(__name__)

# Create router
router = APIRouter()

# Initialize services
class ChatService:
    def __init__(self):
        logger.info("Initializing ChatService and dependencies")
        self.rag_bot = RAGChatbot()
        self.rule_bot = RuleBasedBot()

    def get_response(self, text, source_lang):
        """Get response using rule-based bot first, fallback to RAG"""
        logger.debug("Translating incoming text to English")
        text = translate_to_english(text, source_lang)
        logger.debug("Querying rule-based bot for quick response")
        response = self.rule_bot.get_response(text)

        if not response:
            logger.info("No rule-based response found, falling back to RAG")
            response = self.rag_bot.llmanswer(text)

        return response

    def clear_data(self):
        logger.info("Clearing chatbot indexed data and cache")
        self.rag_bot.clear_data()

# Initialize service
chat_service = ChatService()

@router.post("/respond-audio")
async def respond_to_text(payload: dict):
    """
    Generate a response to the provided text
    """
    try:
        text = payload.get("text", "")
        source_lang = payload.get("source_lang", "")

        if not text:
            raise HTTPException(status_code=400, detail="Text field is required")

        logger.info("Generating response for user input")
        # Get response from chat service
        response = chat_service.get_response(text, source_lang)

        logger.debug("Response generated successfully")
        return {"response": response}
    except HTTPException:
        # re-raise explicit HTTP errors without double-logging as error
        raise
    except Exception as e:
        logger.exception("Response generation error")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

@router.post("/clear-data/")
async def clear_data():
    try:
        chat_service.clear_data()
        return {"message": "Data cleared"}
    except Exception:
        logger.exception("Failed to clear data")
        raise HTTPException(status_code=500, detail="Failed to clear data")

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    try:
        os.makedirs(DOCS_DIR, exist_ok=True)

        # Clear previous files and reset chat data
        for filename in os.listdir(DOCS_DIR):
            file_path = os.path.join(DOCS_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        logger.info("Previous documents removed. Clearing vector store and cache")
        chat_service.clear_data()  # Clear cached data before reloading

        # Save new file
        file_path = os.path.join(DOCS_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info("File saved successfully, reloading documents for indexing")
        chat_service.rag_bot.load_documents()
        return {"message": f"✅ '{file.filename}' uploaded, previous documents cleared and indexed."}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Document upload failed")
        raise HTTPException(status_code=500, detail=f"Failed to upload and process document: {str(e)}")

@router.get("/list-documents/")
async def list_documents():
    try:
        os.makedirs(DOCS_DIR, exist_ok=True)
        files = [f for f in os.listdir(DOCS_DIR) if os.path.isfile(os.path.join(DOCS_DIR, f))]
        logger.debug("Listing documents in docs dir")
        return {"documents": files}
    except Exception as e:
        logger.exception("Failed to list documents")
        raise HTTPException(status_code=500, detail="Failed to retrieve documents.")
