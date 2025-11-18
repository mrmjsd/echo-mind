from deep_translator import GoogleTranslator
from core.logging_config import get_logger

logger = get_logger(__name__)

def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translate text from any supported Indian language to English using deep-translator (Google Translate backend).

    :param text: Text in source language (e.g., Tamil, Malayalam, etc.)
    :param source_lang: Source language code (e.g., 'ta' for Tamil, 'ml' for Malayalam)
    :return: Translated English text
    """
    try:
        translated = GoogleTranslator(source=source_lang.replace("-IN", ""), target='en').translate(text)
        return translated
    except Exception as e:
        logger.exception("Translation error from %s to en", source_lang)
        return text  # fallback to original text
