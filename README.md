## 🎬 Anuvidhi Natipher

**Anuvidhi Natipher** is a Streamlit-powered web app for automatic video translation and dubbing into multiple Indian and world languages.  
It extracts audio from a video, transcribes the speech, translates it, generates dubbed speech in the target language, and merges the new audio back into the video. Subtitles (SRT) are also generated.

---

## 🚀 Features

- **Upload a video** (`.mp4`, `.mov`, `.avi`)
- **Automatic audio extraction** from video
- **Speech-to-text transcription** using Google Speech Recognition
- **Translation** to 15+ languages via Deep Translator
- **Text-to-speech dubbing** with Google TTS
- **Audio time-stretching** to match original segment durations
- **Automatic subtitle (SRT) generation**
- **Download dubbed video and subtitles**
- **Intuitive Streamlit web interface**

---

## 🖥️ Demo

![screenshot](screenshot screenshot of your app here if possible)*

---

## 🛠️ Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/anuvidhi-natipher.git
   cd anuvidhi-natipher
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

---

## 🌐 Usage

1. Open the app in your browser (Streamlit will provide a local URL).
2. Upload a video file (supported: `.mp4`, `.mov`, `.avi`).
3. Select your target language.
4. Adjust silence detection sliders if needed.
5. Click **Dub and Translate Video**.
6. Wait for processing to finish.
7. Preview the dubbed video and download both the video and subtitles (SRT).

---

## 📝 Supported Languages

- Hindi, Bengali, Gujarati, Kannada, Malayalam, Marathi, Nepali, Tamil, Telugu, Urdu, English, Spanish, French, German, Portuguese, Russian, Chinese

---

## 📦 Dependencies

- streamlit
- ffmpeg-python
- pydub
- SpeechRecognition
- deep-translator
- gtts
- numpy
- requests

*(See `requirements.txt` for details.)*

**Note:**  
- FFmpeg must be available in your system PATH.  
- Google services (Speech Recognition & TTS) require an active internet connection.

---

## 📄 License

[MIT License](LICENSE)  
*(Or your chosen license)*

---

## 🤝 Contributing

Pull requests, bug reports, and feature suggestions are welcome!  
Please open an issue or submit a PR.

---

## 🙏 Acknowledgements

- [Streamlit](https://streamlit.io/)
- [pydub](https://github.com/jiaaro/pydub)
- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
- [SpeechRecognition](https://github.com/Uberi/speech_recognition)
- [gTTS](https://github.com/pndurette/gTTS)
- [deep-translator](https://github.com/nidhaloff/deep-translator)

---

## 📧 Contact

For questions or support, contact [your.email@example.com](mailto:your.email@example.com)

---

**Enjoy dubbing and translating videos with Anuvidhi Natipher!**

---
