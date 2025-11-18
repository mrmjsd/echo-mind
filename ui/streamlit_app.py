import streamlit as st
from streamlit_js_eval import streamlit_js_eval          # still needed for Speech‑to‑Text
from utils.api_client import get_audio_response
import requests, time, uuid
from io import BytesIO
from deep_translator import GoogleTranslator
from googletrans import Translator
from gtts import gTTS
import base64

# ------------------- Language Map -------------------
LANG_OPTIONS = {
    "ta-IN": "Tamil",
    "ml-IN": "Malayalam",
    "hi-IN": "Hindi",
    "en-IN": "English",
    "kn-IN": "Kannada",
    "te-IN": "Telugu",
}

# ------------------- Page Setup -------------------
st.set_page_config(page_title="EchoMind", layout="centered")
st.title("🎙️ EchoMind - Your Voice Assistant")

# ------------------- API Configuration -------------------
import os
import pathlib
_in_docker = pathlib.Path("/.dockerenv").exists()
BACKEND_HOST = os.getenv("BACKEND_HOST") or ("backend" if _in_docker else "0.0.0.0")
BACKEND_PORT = os.getenv("BACKEND_PORT", "3030")
API_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api/v1"

# ------------------- Cached Document Fetch -------------------
@st.cache_data(ttl=60)
def get_documents():
    try:
        res = requests.get(f"{API_BASE_URL}/list-documents/")
        if res.status_code == 200:
            return res.json().get("documents", [])
    except:
        return []
    return []

# ------------------- Session State Initialization -------------------
default_state = {
    "conversation": [],
    "active": False,
    "speech_done": False,
    "speech_key": 0,
    "current_state": "idle",
    "uploaded_filename": None,
    "selected_lang": "en-IN"
}
for k, v in default_state.items():
    st.session_state.setdefault(k, v)

# ------------------- Sidebar Upload & Docs -------------------
st.sidebar.header("📄 Upload Knowledge Document")
with st.sidebar.expander("🔌 Backend", expanded=False):
    st.caption(f"API: {API_BASE_URL} (in_docker={_in_docker})")
    try:
        hc = requests.get(f"{API_BASE_URL}/list-documents/", timeout=3)
        st.success("Backend reachable" if hc.ok else f"Backend error: {hc.status_code}")
    except Exception as e:
        st.error(f"Backend not reachable: {e}")
uploaded_file = st.sidebar.file_uploader(
    "Choose a PDF/Text/Doc file", type=["pdf", "txt", "docx"]
)

if uploaded_file is not None and st.sidebar.button("Upload Document"):
    if uploaded_file.name != st.session_state.uploaded_filename:
        with st.spinner("📤 Uploading and indexing document..."):
            try:
                resp = requests.post(
                    f"{API_BASE_URL}/upload-document/",
                    files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                )
                st.session_state.uploaded_filename = uploaded_file.name
                if resp.status_code == 200:
                    st.sidebar.success(f"✅ {uploaded_file.name} uploaded.")
                    get_documents.clear()
                elif resp.status_code == 409:
                    msg = resp.json().get("message", f"{uploaded_file.name} already exists.")
                    st.sidebar.warning(msg)
                else:
                    st.sidebar.error("❌ Upload failed.")
            except Exception as e:
                st.sidebar.error(f"⚠️ Error: {e}")
    else:
        st.sidebar.info(f"📂 '{uploaded_file.name}' already uploaded.")

with st.sidebar.expander("📚 Existing Documents"):
    docs = get_documents()
    if docs:
        for doc in docs:
            st.markdown(f"📄 {doc}")
    else:
        st.markdown("No documents uploaded yet.")

# ------------------- Display Conversation -------------------
if st.session_state.conversation:
    st.subheader("💬 Recent Conversation")
    for ex in st.session_state.conversation[-3:]:
        try:
            tgt = st.session_state.selected_lang.split("-")[0]
            u_text = GoogleTranslator(source="auto", target=tgt).translate(ex["user"])
            a_text = GoogleTranslator(source="en", target=tgt).translate(ex["assistant"])
        except:
            u_text, a_text = ex["user"], ex["assistant"]

        st.markdown(f"🗣️ **You ({LANG_OPTIONS[st.session_state.selected_lang]}):** {u_text}")
        st.markdown(f"🤖 **EchoMind ({LANG_OPTIONS[st.session_state.selected_lang]}):** {a_text}")
        st.divider()

# ------------------- Control Buttons -------------------
col1, col2 = st.columns([1, 3])
with col1:
    if st.session_state.current_state == "idle":
        if st.button("🎙️ Start EchoMind", use_container_width=True):
            st.session_state.current_state = "language_selection"
            st.rerun()
    else:
        if st.button("🔄 Reset", use_container_width=True):
            for k in default_state:
                st.session_state[k] = default_state[k]
            st.rerun()

# ------------------- Language Selection -------------------
if st.session_state.current_state == "language_selection":
    lang = st.selectbox(
        "🌐 Choose Your Language:", LANG_OPTIONS.keys(),
        format_func=lambda x: LANG_OPTIONS[x]
    )
    if st.button("Start Listening"):
        st.session_state.selected_lang = lang
        st.session_state.current_state = "listening"
        st.session_state.speech_key += 1
        st.rerun()

# ------------------- Listening -------------------
elif st.session_state.current_state == "listening":
    with st.status(f"🎤 Listening in {LANG_OPTIONS[st.session_state.selected_lang]}...", expanded=True):
        st.write("Speak now...")
        text = streamlit_js_eval(
            js_expressions=f"""
                (async () => {{
                    return await new Promise((resolve) => {{
                        const recog = new webkitSpeechRecognition();
                        recog.lang = '{st.session_state.selected_lang}';
                        recog.continuous = false;
                        recog.interimResults = false;
                        recog.onresult = (e) => resolve(e.results[0][0].transcript);
                        recog.onerror = () => resolve('');
                        recog.start();
                    }});
                }})()
            """,
            key=f"speech_input_{st.session_state.speech_key}"
        )

        if text and text.strip():
            st.session_state.user_text = text.strip()
            st.session_state.current_state = "processing"
            st.rerun()

# ------------------- Processing -------------------
elif st.session_state.current_state == "processing":
    with st.spinner("⚙️ Processing..."):
        resp = get_audio_response(st.session_state.user_text, st.session_state.selected_lang)
        st.session_state.conversation.append(
            {"user": st.session_state.user_text, "assistant": resp}
        )
        st.session_state.assistant_response = resp
        st.session_state.current_state = "speaking"
        st.rerun()

# ------------------- Speaking (via gTTS) -------------------
elif st.session_state.current_state == "speaking":
    lang_code = st.session_state.selected_lang.split("-")[0]
    original_resp = st.session_state.conversation[-1]["assistant"]

    # 1️⃣ translate assistant reply to the user’s language
    try:
        translated = Translator().translate(original_resp, src="en", dest=lang_code).text
    except Exception as e:
        translated = original_resp
        st.warning(f"⚠️ Translation failed: {e}")

    st.info(f"🗣️ You said: {st.session_state.conversation[-1]['user']}")
    st.success(f"🤖 EchoMind ({LANG_OPTIONS[st.session_state.selected_lang]}): {translated}")

    # 2️⃣ generate MP3 with gTTS
    tts = gTTS(text=translated, lang=lang_code)
    buf = BytesIO()
    tts.write_to_fp(buf)
    audio_bytes = buf.getvalue()
    b64 = base64.b64encode(audio_bytes).decode()

    # 3️⃣ play it silently & detect when it ends
    result = streamlit_js_eval(
        js_expressions=f"""
            (async () => {{
                return await new Promise((resolve) => {{
                    const audio = new Audio("data:audio/mp3;base64,{b64}");
                    audio.autoplay = true;
                    audio.onended  = () => resolve("done");
                    audio.onerror  = () => resolve("done");
                    audio.play();
                }});
            }})()
        """,
        key=f"auto_audio_{st.session_state.speech_key}"
    )

    # 4️⃣ once playback is done, jump back to STT
    if result == "done":
        st.session_state.current_state = "listening"
        st.session_state.speech_key += 1
        st.rerun()

# ------------------- Idle State Instructions -------------------
if st.session_state.current_state == "idle" and not st.session_state.conversation:
    docs = get_documents()
    if docs:
        doc_list = "\n".join(f"- {d}" for d in docs)
        st.markdown(f"""
👋 Hello! I am **EchoMind**, your voice assistant for uploaded documents.

📂 Available documents:
{doc_list}

🎙️ Click **Start EchoMind** to begin speaking!
""")
    else:
        st.markdown("""
👋 Hello! I am **EchoMind**, your voice assistant for uploaded documents.

📄 No documents found. Upload one from the sidebar and then click **Start EchoMind**.
""")
