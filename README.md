# 🎙️ Gnani AI Voice Assistant

A multilingual AI-powered voice assistant built using Gnani AI speech technology and Streamlit.

## 🌟 Project Overview

The Gnani AI Voice Assistant converts spoken audio into text and written text into natural-sounding speech. It supports English, Hindi, and Telugu language options.

## 🚀 Live Demo

[Open Gnani AI Voice Assistant](https://gnani-ai-voice-assistant-9se4qiwtjs6k3dqyezzqv8.streamlit.app/)

## ✨ Features

- Speech-to-Text conversion
- Text-to-Speech generation
- Multilingual language selection
- Multiple AI voice options
- Audio playback
- Downloadable transcription
- Downloadable generated audio

## 🛠️ Technologies Used

- Python
- Streamlit
- Gnani AI APIs
- REST API
- Requests
- python-dotenv

## 🌐 Supported Languages

- English
- Hindi
- Telugu
- Automatic Indic language detection for speech recognition

## 📂 Project Structure

```text
gnani-voice-assistant/
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/DevaHarshini677/gnani-ai-voice-assistant.git
```

2. Navigate to the project directory:

```bash
cd gnani-ai-voice-assistant
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your Gnani API key:

```text
GNANI_API_KEY_ID=your_actual_api_key
```

5. Run the application:

```bash
streamlit run app.py
```

For Streamlit Cloud deployment, configure the API key through the app's Secrets settings.

## 🔐 Security

API credentials are stored using environment variables or Streamlit Secrets. The `.env` file must never be uploaded to GitHub.

## 👩‍💻 Developer

**Deva Harshini**

GitHub: [DevaHarshini677](https://github.com/DevaHarshini677)

## 📌 Project Purpose

Developed as a prototype for the Great Indian AI Internship Challenge.

## 📄 License

This project is intended for educational and demonstration purposes.
