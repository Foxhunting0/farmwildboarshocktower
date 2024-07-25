import streamlit as st
import requests

st.title("🎈 My new app")
st.write("Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io)")

video_path = st.text_input("비디오 경로를 입력하세요:")

if st.button("멧돼지 감지 시작"):
    if video_path:
        # Flask 서버에 요청 보내기
        url = "http://localhost:5000/detect"  # Flask 서버 URL
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
    else:
        st.error("비디오 경로를 입력해야 합니다.")
