import streamlit as st

st.write("BreakWordTraps")

with st.form(key="upload"):
    videos = st.file_uploader(label="Drop the video you want to classify!", accept_multiple_files=True)
    submit = st.form_submit_button(label="Classify")