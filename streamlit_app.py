import streamlit as st
import requests

st.title("🐗 Wild Boar Detection")
st.write("This is Sparta!!! 'Personne n'échappe à mon regard.'")

# CSS 스타일 추가 - 폰트 크기를 2.5배로 설정
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

# HTML 파일을 UTF-8 인코딩으로 읽어옵니다.
def load_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

st.title("멧돼지 감지시 지도에 표기 됩니다.")

# 동영상 파일 업로드 위젯
uploaded_file = st.file_uploader(" ", type=["mp4", "avi", "mov"])

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
    url = f"http://192.168.0.101:8501/fence/{state}"

    try:
        response = requests.post(url)
        if response.status_code == 200:
            st.session_state.fence_state = (state == "on")
            if st.session_state.fence_state:
                image_url = "http://192.168.0.101:8501/fence_image"
                st.image(image_url, caption="하늘에서 정의가 빗발친다.", use_column_width=True)
                 # Show the fence video
                video_url = "http://192.168.0.101:8501/fence_video"
                st.video(video_url)
            else:
                st.write("전기 방벽이 꺼져 있습니다.")
        else:
            st.error(f"서버 오류: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"서버 요청 중 오류 발생: {e}")

if st.session_state.mode == 'manual':
    if uploaded_file is not None:
        # 동영상 재생
        st.video(uploaded_file)
        
    if st.button("전기 방벽 켜기" if not st.session_state.fence_state else "전기 방벽 끄기"):
        toggle_fence("on" if not st.session_state.fence_state else "off")

# 감지 후 지도를 표시하는 함수
def display_maps():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>멧돼지 퇴치 설비 서비스 지역</title>
        <meta charset="utf-8">
        <style>
            #map1, #map2, #map3 {
                height: 500px; /* 지도의 높이 설정 */
                width: 100%;   /* 지도의 너비 설정 */
                margin-bottom: 20px; /* 지도의 사이 간격 설정 */
            }
            body {
                font-family: Arial, sans-serif;
            }
        </style>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    </head>
    <body>
        <h1>멧돼지 출몰 지역</h1>
        <div id="result">Fetching location...</div>
        <div id="map1"></div>
        <div id="map2"></div>
        <div id="map3"></div>

        <script>
            // 페이지 로드 시 자동으로 위치를 가져옴
            window.onload = function() {
                getLocation();
                initializeOtherMaps();
            };

            function getLocation() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(showPosition, showError);
                } else {
                    document.getElementById("result").innerHTML = "Geolocation is not supported by this browser.";
                }
            }

            function showPosition(position) {
                var lat = position.coords.latitude;
                var lon = position.coords.longitude;
                document.getElementById("result").innerHTML = "Latitude: " + lat + "<br>Longitude: " + lon;

                // 지도 표시
                var map1 = L.map('map1').setView([lat, lon], 13);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map1);

                // 현재 위치에 마커와 버블 추가
                L.marker([lat, lon]).addTo(map1)
                    .bindPopup('wild boar!!')
                    .openPopup();

                L.circle([lat, lon], {
                    color: 'blue',
                    fillColor: '#30f',
                    fillOpacity: 0.5,
                    radius: 500 // 버블의 반경
                }).addTo(map1)
                    .bindPopup('Current Location Area');
            }

            function showError(error) {
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        document.getElementById("result").innerHTML = "User denied the request for Geolocation.";
                        break;
                    case error.POSITION_UNAVAILABLE:
                        document.getElementById("result").innerHTML = "Location information is unavailable.";
                        break;
                    case error.TIMEOUT:
                        document.getElementById("result").innerHTML = "The request to get user location timed out.";
                        break;
                    case error.UNKNOWN_ERROR:
                        document.getElementById("result").innerHTML = "An unknown error occurred.";
                        break;
                }
            }

            function initializeOtherMaps() {
                // 첫 번째 추가 지도
                var map2 = L.map('map2').setView([35.5287329, 129.2901099], 13); // 예시 좌표

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map2);

                // 추가 위치에 마커와 버블 추가
                L.marker([35.5287329, 129.2901099]).addTo(map2)
                    .bindPopup('대공원 농장');

                L.circle([35.5287329, 129.2901099], {
                    color: 'green',
                    fillColor: '#0f0',
                    fillOpacity: 0.5,
                    radius: 500 // 버블의 반경
                }).addTo(map2)
                    .bindPopup('대공원 농장 지역');
                
                // 두 번째 추가 지도
                var map3 = L.map('map3').setView([35.5175338, 129.3258761], 13); // 예시 좌표

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map3);

                // 추가 위치에 마커와 버블 추가
                L.marker([35.5175338, 129.3258761]).addTo(map3)
                    .bindPopup('선함호수 농장');

                L.circle([35.5175338, 129.3258761], {
                    color: 'red',
                    fillColor: '#f00',
                    fillOpacity: 0.5,
                    radius: 500 // 버블의 반경
                }).addTo(map3)
                    .bindPopup('선함호수 농장 지역');
            }
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_content, height=1600)


# 자동 모드 - 수동 승인
if st.session_state.mode == 'automatic_manual_approval' and uploaded_file is not None:
    if st.button("아무도 내게서 숨지 못해"):
        # 동영상 재생
        st.video(uploaded_file)
        
        url = "http://192.168.0.101:8501/detect"
       
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
                            detected_image_url = f"http://192.168.0.101:8501/{detected_image_path}"
                            st.image(detected_image_url, caption="감지된 이미지", use_column_width=True)

                        # 위치 정보를 표시할 HTML 콘텐츠 로드
                        display_maps()

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
        image_url = "http://192.168.0.101:8501/fence_image"
        st.image(image_url, caption="하늘에서 정의가 빗발친다.", use_column_width=True)
        video_url = "http://192.168.0.101:8501/fence_video"
        st.video(video_url)

# 자동 모드 - 자동 승인
if st.session_state.mode == 'automatic_approval' and uploaded_file is not None:
    if st.button("아무도 내게서 숨지 못해"):
        # 동영상 재생
        st.video(uploaded_file)
        
        url = "http://192.168.0.101:8501/detect"
        
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
                            detected_image_url = f"http://192.168.0.101:8501/{detected_image_path}"
                            st.image(detected_image_url, caption="감지된 이미지", use_column_width=True)
                        
                        # 전기 방벽 켜기
                        toggle_fence("on")
                        st.session_state.fence_state = True

                        # 위치 정보를 표시할 HTML 콘텐츠 로드
                        display_maps()
                    else:
                        st.warning(data.get("message", "알 수 없는 응답입니다."))
                else:
                    st.error(f"서버와의 통신 오류: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"서버 요청 중 오류 발생: {e}")
