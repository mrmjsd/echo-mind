import requests
import time
try:
    from core.logging_config import get_logger
except Exception:
    # Fallback for Streamlit runtime where backend package path may not be available
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    def get_logger(name):
        return logging.getLogger(name)

import os
import pathlib

logger = get_logger(__name__)

# Resolve backend host/port
# If running inside Docker (/.dockerenv exists) AND no BACKEND_HOST provided,
# default to the docker-compose service name 'backend'. Otherwise default to 0.0.0.0.
_in_docker = pathlib.Path("/.dockerenv").exists()
BACKEND_HOST = os.getenv("BACKEND_HOST") or ("backend" if _in_docker else "0.0.0.0")
BACKEND_PORT = os.getenv("BACKEND_PORT", "3030")
API_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/v1"

# Log resolved API endpoint for easier debugging
logger.debug("API_URL resolved to %s (in_docker=%s)", API_URL, _in_docker)


def transcribe_audio(file_path_or_bytes, use_bytes=False):
    """
    Send audio to backend for transcription.

    Args:
        file_path_or_bytes: Either a file path or audio bytes
        use_bytes: If True, file_path_or_bytes is treated as bytes

    Returns:
        Transcribed text
    """
    start_time = time.time()
    try:
        if use_bytes:
            # Directly send bytes
            response = requests.post(
                f"{API_URL}/transcribe",
                files={"file": ("recording.wav", file_path_or_bytes, "audio/wav")}
            )
        else:
            # Send file from path
            with open(file_path_or_bytes, 'rb') as f:
                response = requests.post(f"{API_URL}/transcribe", files={"file": f})

        if response.status_code == 200:
            end_time = time.time()
            duration = end_time - start_time
            logger.debug("Transcribe response %s in %.2fs", response.status_code, duration)
            return response.json().get("text", "")
        else:
            logger.error("Transcribe error: %s, %s", response.status_code, response.text)
            return f"Error transcribing audio: {response.status_code}"
    except Exception as e:
        logger.exception("Exception in transcribe_audio")
        return f"Error: {str(e)}"


def get_response(text: str) -> tuple[str, str]:
    """Get text response from the API"""
    start_time = time.time()
    try:
        response = requests.post(f"{API_URL}/respond", json={"text": text})
        data = response.json()
        end_time = time.time()
        duration = end_time - start_time
        logger.debug("get_response returned %s in %.2fs", response.status_code, duration)
        return data.get("reply", ""), data.get("audio_path", "")
    except Exception as e:
        logger.exception("Exception in get_response")
        return f"Error: {str(e)}", ""


def get_audio_response(text, source_lang):
    """Get text response for audio input"""
    try:
        if not text or text.isspace():
            return "I couldn't hear anything. Could you please speak again?"

        response = requests.post(f"{API_URL}/respond-audio", json={"text": text, "source_lang": source_lang})

        if response.status_code == 200:
            return response.json().get("response", "I'm not sure how to respond to that.")
        else:
            logger.error("Audio respond error: %s, %s", response.status_code, response.text)
            return f"Error getting response: {response.status_code}"
    except Exception as e:
        logger.exception("Exception in get_audio_response")
        return f"Error: {str(e)}"