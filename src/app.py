from datetime import timedelta
from tempfile import NamedTemporaryFile

import streamlit as st
from moviepy.editor import VideoFileClip

from media_analysis import Analyzer

st.write(
    """
    # :red[wideo]buzdygan
    by **kontentbuzdygan**
    """
)

openai_api_key = st.text_input(
    "OpenAI API key",
    help="Please set up an account and provide your own API key",
    type="password",
)

video = st.file_uploader("Upload the video you want to analyze")

if video:
    st.video(video)

    video_file = NamedTemporaryFile(delete_on_close=False)
    video_file.write(video.getbuffer())
    video_file.close()

    if st.button(label="Analyze", type="primary"):
        clip = VideoFileClip(video_file.name)
        audio_file = NamedTemporaryFile(suffix=".mp3", delete_on_close=False)
        audio_file.close()
        clip.audio.write_audiofile(audio_file.name)

        st.audio(audio_file.name)

        analyzer = Analyzer(openai_api_key)
        transcription = analyzer.transcribe(audio_file.name)

        st.write("## Transcription")

        if transcription.segments:
            for segment in transcription.segments:
                st.write(timedelta(seconds=segment.start), segment.text)

        analysis_results = analyzer.analyze_transcription(transcription.text)

        st.write("## Analysis")
        st.code(analysis_results, wrap_lines=True)
