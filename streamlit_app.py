import streamlit as st
import requests
import os

st.title("🎈 My new app")
st.write("Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io)")

# 동영상 파일 업로드
uploaded_file = st.file_uploader("동영상 파일을 업로드하세요", type=["mp4", "avi", "mov"])

if st.button("멧돼지 감지 시작"):
    if uploaded_file is not None:
        # 임시 파일로 저장
        video_path = f"./{uploaded_file.name}"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Flask 서버에 요청 보내기
        url = "http://58.239.10.48:8501/detect"  # Flask 서버 URL
        response = requests.post(url, json={"video_path": video_path})
        
        if response.status_code == 200:
            data = response.json()
            if data.get("detected"):
                st.success("멧돼지가 감지되었습니다!")
                st.write(data.get("data"))
            else:
                st.warning(data.get("message"))
        else:
            st.error("서버 오류가 발생했습니다.")
        
        # 임시 비디오 파일 삭제
        os.remove(video_path)
    else:
        st.error("동영상 파일을 업로드해야 합니다.")
