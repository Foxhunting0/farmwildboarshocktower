import streamlit as st
import requests
import os
import uuid

st.title("🎈 My new app")
st.write("Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io)")

# 동영상 파일 업로드
uploaded_file = st.file_uploader("동영상 파일을 업로드하세요", type=["mp4", "avi", "mov"])

if st.button("멧돼지 감지 시작"):
    if uploaded_file is not None:
        # 임시 파일로 저장 (고유한 이름 추가)
        video_path = f"./{uuid.uuid4()}_{uploaded_file.name}"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Flask 서버에 파일 전송
        url = "http://58.239.10.48:8501/detect"  # Flask 서버 URL
        with open(video_path, "rb") as f:
            response = requests.post(url, files={"video": (uploaded_file.name, f, uploaded_file.type)})
        
        if response.status_code == 200:
            data = response.json()
            if data.get("detected"):
                st.success("멧돼지가 감지되었습니다!")
                st.write(data.get("message"))  # 감지된 데이터 표시
            else:
                st.warning(data.get("message"))
        else:
            st.error(f"서버 오류가 발생했습니다. 상태 코드: {response.status_code}")
        
        # 임시 비디오 파일 삭제 (오류 처리 추가)
        try:
            os.remove(video_path)
        except Exception as e:
            st.error(f"비디오 파일 삭제 중 오류 발생: {e}")
    else:
        st.error("동영상 파일을 업로드해야 합니다.")
