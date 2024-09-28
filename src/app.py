import streamlit as st
from moviepy.editor import VideoFileClip
from tempfile import NamedTemporaryFile
from media_analysis import Analyzer
from datetime import timedelta

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
    video_tmp = NamedTemporaryFile()
    video_tmp.write(video.getbuffer())

    st.video(video_tmp.name)

    if st.button("Analyze", type="primary"):
        clip = VideoFileClip(video_tmp.name)
        audio_tmp = NamedTemporaryFile(suffix=".mp3")
        clip.audio.write_audiofile(audio_tmp.name)

        # st.audio(audio_tmp.name)

        analyzer = Analyzer(openai_api_key)
        transcription = analyzer.transcribe(audio_tmp.name)

        st.write("## Transcription")

        if transcription.segments:
            for segment in transcription.segments:
                st.write(timedelta(seconds=segment.start), segment.text)

        analysis_results = analyzer.analyze_transcription(transcription.text)

        st.write("## Analysis")
        st.code(analysis_results, wrap_lines=True)
