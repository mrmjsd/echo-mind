import os
import time
from groq import Groq, GroqError
from  core.config import GROQ_API_KEY
from core.logging_config import get_logger

logger = get_logger(__name__)
logger = get_logger(__name__)

class GroqClient:
    def __init__(self, model="llama-3.3-70b-versatile", max_retries=3):
        # Initialize the Groq client
        # The client handles retries and timeouts automatically
        self.client = Groq(
            api_key=GROQ_API_KEY,
            max_retries=max_retries,
            timeout=30.0  # Set timeout to 30 seconds, matching original code
        )
        self.model = model
        # max_retries is handled by the client, but we can store it if needed
        self.max_retries = max_retries 
        logger.info("Initialized GroqClient with model %s and max_retries=%d", model, max_retries)

    def generate_answer(self, context: str, question: str) -> str:
        try:
            prompt = f"""You are a helpful assistant. Answer the question based only on the following context:

            Context:
            {context}

            Question: {question}
            Answer:"""

            logger.debug("Calling Groq API (retries managed by client)")
            
            # Use the Groq client to create the chat completion
            chat_completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant try to answer in a one sentence."},
                    {"role": "user", "content": prompt}
                ],
                temperature=1.0
            )
            
            answer = chat_completion.choices[0].message.content.strip()
            logger.debug("Groq API call succeeded")
            return answer

        except GroqError as e:
            logger.error("Groq API call failed after %d retries: %s", self.max_retries, str(e))
            raise  # Re-raise the exception after logging
        except Exception as e:
            logger.error("An unexpected error occurred during Groq API call: %s", str(e))
            raise # Re-raise other unexpected errors
