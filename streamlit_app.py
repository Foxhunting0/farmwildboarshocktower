import streamlit as st
import requests

st.title("🐗 Wild Boar Detection")
st.write("This is Sparta!!! 'Personne n'échappe à mon regard.'")

# CSS 스타일 추가 - 폰트 크기를 1.5배로 설정
st.markdown(
    """
    <style>
    body {
        font-size: 2.5em;  /* 기본 폰트 크기 조정 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 배경화면 CSS 추가
image_url3 = 'https://i.ytimg.com/vi/SJa5_DoaDGk/maxresdefault.jpg'
st.image(image_url3, use_column_width=True)

# 동영상 파일 업로드 위젯
uploaded_file = st.file_uploader("동영상을 업로드하세요:", type=["mp4", "avi", "mov"])

# 전기 방벽 상태 초기화
if 'fence_state' not in st.session_state:
    st.session_state.fence_state = False

# 모드 상태 초기화
if 'mode' not in st.session_state:
    st.session_state.mode = 'manual'

# 모드 전환 버튼
if st.button("반자동-자동-수동"):
    if st.session_state.mode == 'manual':
        st.session_state.mode = 'automatic_manual_approval'
    elif st.session_state.mode == 'automatic_manual_approval':
        st.session_state.mode = 'automatic_approval'
    else:
        st.session_state.mode = 'manual'
    st.success(f"{st.session_state.mode} 모드로 전환되었습니다.")

# 현재 모드 상태 출력
st.write(f"현재 모드: {st.session_state.mode}")

# 전기 방벽 온오프 버튼
def toggle_fence(state):
    url = f"http://192.168.0.75:8501/fence/{state}"

    try:
        response = requests.post(url)
        if response.status_code == 200:
            st.session_state.fence_state = (state == "on")
            if st.session_state.fence_state:
                image_url = "http://192.168.0.156:8501/fence_image"
                st.image(image_url, caption="하늘에서 정의가 빗발친다.", use_column_width=True)
            else:
                st.write("전기 방벽이 꺼져 있습니다.")
        else:
            st.error(f"서버 오류: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"서버 요청 중 오류 발생: {e}")

if st.session_state.mode == 'manual':
    if st.button("전기 방벽 켜기" if not st.session_state.fence_state else "전기 방벽 끄기"):
        toggle_fence("on" if not st.session_state.fence_state else "off")

# 자동 모드 - 수동 승인
if st.session_state.mode == 'automatic_manual_approval' and uploaded_file is not None:
    if st.button("아무도 내게서 숨지 못해"):
        url = "http://192.168.0.156:8501/detect"
       
        with st.spinner("서버에 요청 중..."):
            try:
                response = requests.post(url, files={"video": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)})
                if response.status_code == 200:
                    data = response.json()
                    if data.get("detected"):
                        st.success("목표를 포착했다!")
                        st.write(data["message"])
                        detected_image_path = data.get("image_url")
                        if detected_image_path:
                            detected_image_url = f"http://192.168.0.75:8501/{detected_image_path}"
                            st.image(detected_image_url, caption="감지된 이미지", use_column_width=True)

                        if st.button("승인"):
                            toggle_fence("on")
                            st.session_state.fence_state = True

                    else:
                        st.warning(data.get("message", "알 수 없는 응답입니다."))
                else:
                    st.error(f"서버와의 통신 오류: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"서버 요청 중 오류 발생: {e}")

    if st.session_state.fence_state:
        image_url = "http://192.168.0.38:8501/fence_image"
        st.image(image_url, caption="하늘에서 정의가 빗발친다.", use_column_width=True)

# 자동 모드 - 자동 승인
if st.session_state.mode == 'automatic_approval' and uploaded_file is not None:
    if st.button("아무도 내게서 숨지 못해"):
        url = "http://192.168.0.156:8501/detect"
        
        with st.spinner("서버에 요청 중..."):
            try:
                response = requests.post(url, files={"video": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)})
                if response.status_code == 200:
                    data = response.json()
                    if data.get("detected"):
                        st.success("목표를 포착했다!")
                        st.write(data["message"])
                        detected_image_path = data.get("image_url")
                        if detected_image_path:
                            detected_image_url = f"http://192.168.0.156:8501/{detected_image_path}"
                            st.image(detected_image_url, caption="감지된 이미지", use_column_width=True)
                        toggle_fence("on")
                    else:
                        st.warning(data.get("message", "알 수 없는 응답입니다."))
                else:
                    st.error(f"서버와의 통신 오류: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"서버 요청 중 오류 발생: {e}")

# 전원 끄기 버튼 클릭 시 실행
if st.button("전원 끄기"):
    st.success("전원이 꺼졌습니다.")
    st.session_state.fence_state = False
    st.write("전기 방벽이 꺼져 있습니다.")
