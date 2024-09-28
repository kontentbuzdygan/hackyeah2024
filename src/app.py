import streamlit as st

st.write("BreakWordTraps")

videos = st.file_uploader(label="Drop the video you want to classify!", accept_multiple_files=True)
st.button(label="Classify")

if videos:
    for video in videos:
        st.video(video)