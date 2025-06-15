import streamlit as st
import tempfile
import os
import ffmpeg
from pydub import AudioSegment, silence
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import subprocess

st.title("🎬 Anuvidhi Natipher")

def extract_audio(video_path, audio_path):
    try:
        ffmpeg.input(video_path).output(audio_path, format="wav").run(overwrite_output=True)
    except Exception as e:
        st.exception(e)
        raise

def get_audio_duration(audio_path):
    try:
        probe = ffmpeg.probe(audio_path)
        return float(probe['format']['duration'])
    except Exception as e:
        st.exception(e)
        raise

def split_audio(audio_path, min_silence_len=700, silence_thresh=-40):
    sound = AudioSegment.from_wav(audio_path)
    nonsilent_ranges = silence.detect_nonsilent(sound, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    segments = []
    for start, end in nonsilent_ranges:
        segments.append(sound[start:end])
    return segments, nonsilent_ranges

def speech_to_text(segment):
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        tmp_audio_path = tmp_audio.name
    segment.export(tmp_audio_path, format="wav")
    try:
        with sr.AudioFile(tmp_audio_path) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            text = ""
        except sr.RequestError as e:
            text = ""
    finally:
        os.unlink(tmp_audio_path)
    return text

def translate_text(text, target_lang="hi"):
    if not text.strip():
        return ""
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        st.warning(f"Translation failed: {e}")
        return text

def text_to_speech(text, lang="hi"):
    if not text.strip():
        return AudioSegment.silent(duration=500)
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
            tmp_mp3_path = tmp_mp3.name
        tts.save(tmp_mp3_path)
        tts_audio = AudioSegment.from_file(tmp_mp3_path, format="mp3")
        os.unlink(tmp_mp3_path)
        return tts_audio
    except Exception as e:
        st.warning(f"TTS failed: {e}")
        return AudioSegment.silent(duration=500)

def time_stretch_audio(segment, target_duration_ms):
    if len(segment) == 0 or target_duration_ms == 0:
        return AudioSegment.silent(duration=target_duration_ms)
    speed = len(segment) / target_duration_ms
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_in, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_out:
        tmp_in_path = tmp_in.name
        tmp_out_path = tmp_out.name
    segment.export(tmp_in_path, format="wav")
    filters = []
    s = speed
    while s < 0.5:
        filters.append("atempo=0.5")
        s /= 0.5
    while s > 2.0:
        filters.append("atempo=2.0")
        s /= 2.0
    filters.append(f"atempo={s}")
    filter_str = ",".join(filters)
    try:
        ffmpeg.input(tmp_in_path).output(tmp_out_path, af=filter_str).overwrite_output().run()
        stretched = AudioSegment.from_file(tmp_out_path, format="wav")
    except Exception as e:
        st.warning(f"FFmpeg time-stretch failed, using original audio: {e}")
        stretched = AudioSegment.from_file(tmp_in_path, format="wav")
    os.unlink(tmp_in_path)
    os.unlink(tmp_out_path)
    return stretched

def merge_audio_segments(segments, start_times, total_duration):
    merged_audio = AudioSegment.silent(duration=total_duration)
    for seg, start in zip(segments, start_times):
        merged_audio = merged_audio.overlay(seg, position=start)
    return merged_audio

def remove_audio_from_video(video_path, output_path):
    try:
        ffmpeg.input(video_path).output(output_path, an=None, vcodec='copy').run(overwrite_output=True)
    except Exception as e:
        st.warning(f"FFmpeg remove audio failed: {e}")
        raise

def add_audio_to_video(video_path, audio_path, output_path):
    # Try ffmpeg-python first, then fallback to subprocess if error
    video_stream = ffmpeg.input(video_path)
    audio_stream = ffmpeg.input(audio_path)
    try:
        (
            ffmpeg
            .output(video_stream, audio_stream, output_path,
                    vcodec='copy',
                    acodec='aac',
                    map=['0:v:0', '1:a:0'],
                    shortest=None)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        st.warning("ffmpeg-python failed, trying subprocess fallback...")
        command = [
            "ffmpeg",
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            '-y',
            output_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            st.error("ffmpeg subprocess failed:\n" + result.stderr.decode())
            raise RuntimeError("ffmpeg failed to mux audio and video.")

def write_srt(subs, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, (start, end, text) in enumerate(subs, 1):
            f.write(f"{idx}\n")
            f.write(f"{ms_to_srt(start)} --> {ms_to_srt(end)}\n")
            f.write(f"{text}\n\n")

def ms_to_srt(ms):
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

# --- Streamlit UI ---
target_lang = st.selectbox(
    "Select target language",
    [
        ("Hindi", "hi"),
        ("Bengali", "bn"),
        ("Gujarati", "gu"),
        ("Kannada", "kn"),
        ("Malayalam", "ml"),
        ("Marathi", "mr"),
        ("Nepali", "ne"),
        ("Tamil", "ta"),
        ("Telugu", "te"),
        ("Urdu", "ur"),
        ("English", "en"),
        ("Spanish", "es"),
        ("French", "fr"),
        ("German", "de"),
        ("Portuguese", "pt"),
        ("Russian", "ru"),
        ("Chinese", "zh-CN"),
    ]
)

video_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
min_silence_len = st.slider("Min silence length (ms)", 100, 20000, 700, step=100)
silence_thresh = st.slider("Silence threshold (dB)", -80, 0, -40, step=1)

if st.button("Dub and Translate Video") and video_file:
    with st.spinner("Processing..."):
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                video_path = os.path.join(tmpdir, "input_video.mp4")
                with open(video_path, "wb") as f:
                    f.write(video_file.read())
                audio_path = os.path.join(tmpdir, "audio.wav")
                extract_audio(video_path, audio_path)
                total_duration = int(get_audio_duration(audio_path) * 1000)
                st.info("Splitting audio into segments...")
                segments_audio, nonsilent_ranges = split_audio(audio_path, min_silence_len, silence_thresh)
                st.write(f"Detected {len(segments_audio)} segments.")

                dubbed_segments = []
                start_times = []
                srt_subs = []
                for i, (segment, (start, end)) in enumerate(zip(segments_audio, nonsilent_ranges)):
                    st.info(f"Processing segment {i+1}/{len(segments_audio)}...")
                    text = speech_to_text(segment)
                    translated = translate_text(text, target_lang=target_lang[1])
                    tts_audio = text_to_speech(translated, lang=target_lang[1])
                    tts_stretched = time_stretch_audio(tts_audio, end - start)
                    dubbed_segments.append(tts_stretched)
                    start_times.append(start)
                    srt_subs.append((start, end, translated))
                    st.write(f"Segment {i+1}: {text} → {translated}")

                st.info("Merging dubbed audio segments...")
                merged_audio = merge_audio_segments(dubbed_segments, start_times, total_duration)
                dubbed_audio_path = os.path.join(tmpdir, "dubbed_audio.wav")
                merged_audio.export(dubbed_audio_path, format="wav")

                st.info("Removing original audio and merging dubbed audio with video...")
                no_audio_video_path = os.path.join(tmpdir, "video_no_audio.mp4")
                remove_audio_from_video(video_path, no_audio_video_path)
                dubbed_video_path = os.path.join(tmpdir, "dubbed_video.mp4")
                add_audio_to_video(no_audio_video_path, dubbed_audio_path, dubbed_video_path)

                st.info("Generating SRT subtitles...")
                srt_path = os.path.join(tmpdir, "subtitles.srt")
                write_srt(srt_subs, srt_path)

                with open(dubbed_video_path, "rb") as f:
                    video_bytes = f.read()
                with open(srt_path, "rb") as f:
                    srt_bytes = f.read()
                st.session_state['dubbed_video'] = video_bytes
                st.session_state['subtitles_srt'] = srt_bytes
                st.success("Dubbed video and subtitles ready!")
        except Exception as e:
            st.exception(e)
            
if 'dubbed_video' in st.session_state and 'subtitles_srt' in st.session_state:
    st.video(st.session_state['dubbed_video'])
    st.download_button("Download Dubbed Video", st.session_state['dubbed_video'], file_name="dubbed_video.mp4", key="download_video")
    st.download_button("Download Subtitles (SRT)", st.session_state['subtitles_srt'], file_name="subtitles.srt", key="download_srt")

