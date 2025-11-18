# EchoMind

**EchoMind** is a local-first, AI-powered voice assistant built with Python and FastAPI. It integrates Vosk for speech-to-text (STT), LangChain for natural language understanding, FAISS for semantic search, and Coqui TTS for text-to-speech (TTS). This modular architecture allows for flexible, private, and efficient voice interactions without relying on external services.

## Features

- **Speech Recognition (STT):** Utilizes Vosk for offline, real-time transcription of speech to text.
- **Natural Language Understanding (NLU):** Employs LangChain to process and understand user intents, supporting both rule-based and LLM-based approaches.
- **Semantic Search:** Integrates FAISS to perform efficient similarity searches, enhancing intent matching and information retrieval.
- **Text-to-Speech (TTS):** Uses Coqui TTS to generate natural-sounding speech responses.
- **Modular Architecture:** Designed following SOLID principles for maintainability and scalability.
- **Local-First Processing:** Ensures user data privacy by performing all processing on-device without the need for internet connectivity.

## Architecture Overview

The system comprises the following components:

1. **Speech-to-Text (STT):** Captures and transcribes user speech input using Vosk.
2. **Natural Language Understanding (NLU):** Processes transcribed text to determine user intent via LangChain.
3. **Semantic Search:** Utilizes FAISS to retrieve relevant information based on user queries.
4. **Response Generation:** Constructs appropriate responses using retrieved information and predefined rules or LLMs.
5. **Text-to-Speech (TTS):** Converts text responses into speech using Coqui TTS for audio playback.
   ![image](https://github.com/user-attachments/assets/88505199-314c-48c4-8977-f5361ddceeb5)


## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/EchoMind.git
   cd EchoMind
   ```

2. **Set Up a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download Necessary Models:**

   - **Vosk Model:** Download the appropriate language model from the [Vosk Models Repository](https://alphacephei.com/vosk/models) and place it in the `models/vosk` directory.
   - **Coqui TTS Model:** Follow the [Coqui TTS documentation](https://github.com/coqui-ai/TTS) to download and set up the required models in the `models/coqui` directory.

## Usage

1. **Start the FastAPI Server:**

   ```bash
   uvicorn app.main:app --reload
   ```

2. **Interact with the API:**

   - **Speech-to-Text:** Send a POST request to `/stt` with an audio file to receive the transcribed text.
   - **Text-to-Speech:** Send a POST request to `/tts` with text input to receive the generated speech audio.
   - **Conversational Interface:** Use the `/chat` endpoint to send text queries and receive audio responses.

## API Endpoints

- `POST /stt`: Accepts audio input and returns transcribed text.
- `POST /tts`: Accepts text input and returns synthesized speech audio.
- `POST /chat`: Accepts text input, processes it through the NLU and semantic search components, and returns a spoken response.

## Configuration

Configuration settings, such as model paths and API parameters, can be adjusted in the `config.py` file located in the `app/core` directory.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgments

- [Vosk Speech Recognition Toolkit](https://github.com/alphacep/vosk-api)
- [LangChain Framework](https://github.com/hwchase17/langchain)
- [FAISS Library](https://github.com/facebookresearch/faiss)
- [Coqui TTS](https://github.com/coqui-ai/TTS)

---
