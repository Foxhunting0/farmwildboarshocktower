import streamlit as st
import requests

# 초기 상태 설정
if 'fence_state' not in st.session_state:
    st.session_state.fence_state = False

# 사이드바 추가
st.sidebar.title("설정")
uploaded_file = st.sidebar.file_uploader("비디오 파일 업로드", type=["mp4", "avi"])

# 사용자 안내 메시지
st.info("비디오를 업로드한 후 '아무도 내게서 숨지 못해' 버튼을 눌러 감지하고, 승인 후 전기 방벽을 켭니다.")

# 스타일링 추가
st.markdown(
    """
    <style>
    .custom-button {
        background-color: #4CAF50; /* Green */
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 자동 모드 - 수동 승인
if uploaded_file is not None:
    if st.button("아무도 내게서 숨지 못해"):  # 감지 버튼
        url = "http://192.168.0.75:8501/detect"
        
        with st.spinner("서버에 요청 중..."):
            try:
                response = requests.post(url, files={"video": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)})
                if response.status_code == 200:
                    data = response.json()
                    if data.get("detected"):
                        st.success("목표를 포착했습니다!", icon="✅")
                        st.write(data["message"])  # 감지된 데이터 표시
                        detected_image_path = data.get("image_url")
                        if detected_image_path:
                            detected_image_url = f"http://192.168.0.75:8501/{detected_image_path}"
                            
                            # 이미지와 승인 버튼을 나란히 배치
                            col1, col2 = st.columns(2)

                            with col1:
                                st.image(detected_image_url, caption="감지된 이미지", use_column_width=True)

                            with col2:
                                if st.button("승인", key="approve_button", css_class="custom-button"):
                                    toggle_fence("on")  # 전기 방벽 켜기
                                    st.session_state.fence_state = True  # 전기 방벽 상태 업데이트
                    else:
                        st.warning("감지된 데이터가 없습니다.", icon="⚠️")
                else:
                    st.error(f"서버와의 통신 오류: {response.status_code}, 응답 내용: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"서버 요청 중 오류 발생: {e}")

    # 승인 후 전기 방벽 이미지 표시
    if st.session_state.fence_state:  # 전기 방벽이 켜졌다면
        image_url = "http://192.168.0.75:8501/fence_image"
        st.image(image_url, caption="전기 방벽 켜짐", use_column_width=True)
