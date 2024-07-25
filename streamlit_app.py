import streamlit as st
import requests

st.title("🎈 My new app")
st.write("Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io)")

video_path = st.text_input("비디오 경로를 입력하세요:")

if st.button("멧돼지 감지 시작"):
    if video_path:
       
