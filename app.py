
import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

API_KEY = os.getenv("GNANI_API_KEY_ID")

STT_URL = "https://api.vachana.ai/stt/v3"
TTS_URL = "https://api.vachana.ai/api/v1/tts/inference"

# Page configuration
st.set_page_config(
    page_title="Gnani AI Voice Assistant",
    page_icon="🎙️",
    layout="centered",
)


# Extract text from different Gnani API response formats
def extract_transcript(result):
    if isinstance(result, str):
        return result.strip()

    if isinstance(result, list):
        parts = [extract_transcript(item) for item in result]
        return "\n".join(part for part in parts if part)

    if isinstance(result, dict):
        # Direct transcript
        transcript = result.get("transcript")

        if isinstance(transcript, str) and transcript.strip():
            return transcript.strip()

        # Transcript organized by language
        if isinstance(transcript, dict):
            for text in transcript.values():
                if isinstance(text, str) and text.strip():
                    return text.strip()

        # Alternative output format
        output = result.get("output")

        if isinstance(output, dict):
            literal = output.get("literal")

            if isinstance(literal, str) and literal.strip():
                return literal.strip()

            if isinstance(literal, dict):
                for text in literal.values():
                    if isinstance(text, str) and text.strip():
                        return text.strip()

        # Other possible response fields
        for key in (
            "text",
            "transcription",
            "recognized_text",
            "utterance",
        ):
            value = result.get(key)

            if isinstance(value, str) and value.strip():
                return value.strip()

        # Search nested response fields
        for key in ("data", "result", "results"):
            value = result.get(key)

            if isinstance(value, (dict, list)):
                extracted = extract_transcript(value)

                if extracted:
                    return extracted

    return ""


# Display API errors safely
def show_api_error(response, service_name):
    st.error(
        f"{service_name} API error: HTTP {response.status_code}"
    )

    if response.status_code == 400:
        st.info(
            "Check the language, voice, model, and request parameters."
        )
    elif response.status_code in (401, 403):
        st.info(
            "Check whether your API key is correct and has permission."
        )
    elif response.status_code == 429:
        st.info(
            "The API request limit may have been reached. Try again later."
        )
    elif response.status_code == 504:
        st.info(
            "The API gateway timed out. Try again with a shorter request."
        )

    try:
        st.json(response.json())
    except ValueError:
        st.code(response.text[:2000])


# Application heading
st.title("🎙️ Gnani AI Voice Assistant")
st.markdown("### Speak naturally. Understand clearly.")

st.write(
    "Convert speech into text and written text into audio "
    "using Gnani AI speech technology."
)

# Check API key
if not API_KEY or API_KEY == "YOUR_REAL_API_KEY":
    st.error(
        "API key not found. Add your real API key to the .env file "
        "in the same folder as app.py."
    )
    st.code("GNANI_API_KEY_ID=your_actual_api_key")
    st.stop()

st.divider()

# Two main features
stt_tab, tts_tab = st.tabs(
    ["🎤 Speech to Text", "🔊 Text to Speech"]
)


# =========================================================
# SPEECH TO TEXT
# =========================================================
with stt_tab:
    st.header("🎤 Speech to Text")

    st.write(
        "Upload an audio recording and convert spoken words into text."
    )

    language = st.selectbox(
        "Select audio language",
        [
            "Automatic (Indic)",
            "English",
            "Hindi",
            "Telugu",
        ],
        key="stt_language",
    )

    language_codes = {
        "Automatic (Indic)": "indic-auto",
        "English": "en-IN",
        "Hindi": "hi-IN",
        "Telugu": "te-IN",
    }

    audio_file = st.file_uploader(
        "Choose an audio file",
        type=["wav", "mp3", "m4a", "ogg", "flac", "aac"],
        key="audio_upload",
    )

    if audio_file is not None:
        st.audio(audio_file)

        st.caption(
            f"Selected file: {audio_file.name}"
        )

    if st.button(
        "Transcribe Audio",
        type="primary",
        key="transcribe_button",
    ):
        if audio_file is None:
            st.warning("Please upload an audio file first.")

        else:
            selected_language = language_codes[language]

            stt_data = {
                "language_code": selected_language,
                "format": "transcribe",
                "itn_native_numerals": "true",
            }

            if selected_language == "indic-auto":
                stt_data["multi_lang_codes"] = (
                    "en-IN,hi-IN,te-IN"
                )
                stt_data["preferred_language"] = "en-IN"
            else:
                stt_data["preferred_language"] = selected_language

            try:
                with st.spinner("Transcribing your audio..."):
                    response = requests.post(
                        STT_URL,
                        headers={
                            "X-API-Key-ID": API_KEY,
                        },
                        files={
                            "audio_file": (
                                audio_file.name,
                                audio_file.getvalue(),
                                audio_file.type
                                or "application/octet-stream",
                            )
                        },
                        data=stt_data,
                        timeout=(15, 120),
                    )

                if response.ok:
                    try:
                        result = response.json()
                    except ValueError:
                        st.error(
                            "The API returned an invalid response."
                        )
                        st.code(response.text[:2000])
                    else:
                        if (
                            isinstance(result, dict)
                            and result.get("success") is False
                        ):
                            st.error("Transcription failed.")
                            st.json(result)

                        else:
                            transcript = extract_transcript(result)

                            if transcript:
                                st.success(
                                    "Transcription completed!"
                                )

                                st.text_area(
                                    "Recognized text",
                                    value=transcript,
                                    height=180,
                                    key="recognized_text",
                                )

                                st.download_button(
                                    "📥 Download transcription",
                                    data=transcript.encode("utf-8"),
                                    file_name="transcription.txt",
                                    mime="text/plain",
                                )

                            else:
                                st.warning(
                                    "The API responded, but no non-empty "
                                    "transcript was found."
                                )
                                st.write(
                                    "Check the response below to see "
                                    "which language returned text."
                                )
                                st.json(result)

                else:
                    show_api_error(response, "STT")

            except requests.Timeout:
                st.error(
                    "The STT request timed out. Try a shorter "
                    "audio recording."
                )

            except requests.RequestException as error:
                st.error(
                    f"Could not connect to the STT API: {error}"
                )


# =========================================================
# TEXT TO SPEECH
# =========================================================
with tts_tab:
    st.header("🔊 Text to Speech")

    st.write(
        "Enter text, select a language and voice, and generate audio."
    )

    tts_language = st.selectbox(
        "Select output language",
        ["English", "Hindi", "Telugu"],
        key="tts_language",
    )

    language_codes_tts = {
        "English": "en-IN",
        "Hindi": "hi-IN",
        "Telugu": "te-IN",
    }

    language_code = language_codes_tts[tts_language]

    # Voices supported by the timbre-v2.5 model.
    voice_options = [
        "Kartik",
        "Deepak",
        "Pranav",
        "Nalini",
        "Bhavna",
        "Yashvi",
        "Vikrant",
        "Aarohi",
        "Roopesh",
        "Jwala",
        "Chitra",
        "Urmila",
        "Omkar",
        "Gauri",
        "Madhuri",
        "Radhika",
    ]

    voice_name = st.selectbox(
        "Select voice",
        voice_options,
        key="tts_voice",
    )

    text_input = st.text_area(
        "Enter your text",
        placeholder=(
            "Hello! Welcome to my multilingual AI voice assistant."
        ),
        max_chars=800,
        height=140,
        key="tts_text",
    )

    st.caption(
        f"Characters: {len(text_input)} / 800"
    )

    if st.button(
        "Generate Speech",
        type="primary",
        key="generate_speech_button",
    ):
        if not text_input.strip():
            st.warning("Please enter some text.")

        else:
            payload = {
                "text": text_input.strip(),
                "voice": voice_name,
                "model": "timbre-v2.5",
                "language": language_code,
                "speed": 1.0,
                "audio_config": {
                    "sample_rate": 48000,
                    "num_channels": 1,
                    "sample_width": 2,
                    "encoding": "linear_pcm",
                    "container": "wav",
                },
            }

            try:
                with st.spinner("Generating speech..."):
                    response = requests.post(
                        TTS_URL,
                        headers={
                            "X-API-Key-ID": API_KEY,
                            "Content-Type": "application/json",
                        },
                        json=payload,
                        timeout=(15, 120),
                    )

                if response.ok:
                    content_type = response.headers.get(
                        "Content-Type", ""
                    ).lower()

                    is_wav = response.content[:4] == b"RIFF"
                    is_audio = content_type.startswith("audio/")

                    if is_audio or is_wav:
                        audio_bytes = response.content

                        st.success(
                            "Speech generated successfully!"
                        )

                        st.audio(
                            audio_bytes,
                            format="audio/wav",
                        )

                        st.download_button(
                            "📥 Download audio",
                            data=audio_bytes,
                            file_name="gnani_speech.wav",
                            mime="audio/wav",
                        )

                    else:
                        st.warning(
                            "The API returned a non-audio response. "
                            "Check the response below."
                        )

                        try:
                            st.json(response.json())
                        except ValueError:
                            st.code(response.text[:2000])

                else:
                    show_api_error(response, "TTS")

            except requests.Timeout:
                st.error(
                    "The TTS request timed out. Please try again."
                )

            except requests.RequestException as error:
                st.error(
                    f"Could not connect to the TTS API: {error}"
                )


# Footer
st.divider()

st.caption(
    "Prototype for the Great Indian AI Internship Challenge. "
    "API usage may consume programme credits."
)
