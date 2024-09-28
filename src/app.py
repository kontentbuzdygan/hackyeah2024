import dotenv
import streamlit as st
from moviepy.editor import VideoFileClip
from tempfile import NamedTemporaryFile
from media_analysis import analyze_audio

dotenv.load_dotenv()

st.write("BreakWordTraps")
video = st.file_uploader(label="Drop the video you want to classify!")

if video:
    video_tmp = NamedTemporaryFile()
    video_tmp.write(video.getbuffer())

    st.video(video_tmp.name)

    if st.button(label="Classify!", type="primary"):
        clip = VideoFileClip(video_tmp.name)
        audio_tmp = NamedTemporaryFile(suffix=".mp3")
        clip.audio.write_audiofile(audio_tmp.name)

        # st.audio(audio_tmp.name)

        analysis = analyze_audio(audio_tmp.name)
        st.code(analysis.choices[0].message.parsed, wrap_lines=True)
