import streamlit as st
import requests

st.title("🐗 Wild Boar Detection")
st.write("This is Sparta!!!")

# 동영상 파일 업로드 위젯
uploaded_file = st.file_uploader("동영상을 업로드하세요:", type=["mp4", "avi", "mov"])

# 전기 방벽 이미지 경로
electric_fence_image_path = "C:/Users/KDP007/Desktop/e_w.jpg"

if st.button("아무도 내게서 숨지 못해"):
    if uploaded_file is not None:
        # Flask 서버의 URL을 설정합니다.
        url = "http://192.168.0.75:8501/detect"  # Flask 서버의 URL
        
        # 서버 요청을 보낼 때 로딩 스피너 표시
        with st.spinner("서버에 요청 중..."):
            try:
                # Flask 서버에 파일 전송
                response = requests.post(url, files={"video": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)})
                
                # 응답 처리
                if response.status_code == 200:
                    data = response.json()
                    if "detected" in data and data["detected"]:
                        st.success("멧돼지가 감지되었습니다!")
                        st.write(data["message"])  # 감지된 데이터 표시
                        
                        # 전기 방벽 이미지 표시
                        st.image(electric_fence_image_path, caption="전기 방벽", use_column_width=True)

                        # 감지된 이미지 표시 (서버에서 반환된 이미지 경로 사용)
                        detected_image_path = data.get("image_path")
                        if detected_image_path:
                            st.image(detected_image_path, caption="감지된 이미지", use_column_width=True)
                    else:
                        st.warning(data["message"])
                else:
                    st.error(f"서버와의 통신 오류: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"서버 요청 중 오류 발생: {e}")
    else:
        st.error("동영상을 업로드해주세요.")
