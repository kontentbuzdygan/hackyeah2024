import streamlit as st

st.write("BreakWordTraps")

videos = st.file_uploader("Drop the video you want to classify!", accept_multiple_files=True)