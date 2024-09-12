import streamlit as st
import cv2
import tempfile
import os
import requests
from ultralytics import YOLO

pt = 'farm.pt'
model = YOLO(pt)

# 전기 방벽 모드 초기화
automatic_mode = True  # 기본값을 자동 모드로 설정
electric_fence_active = False  # 전기 방벽 상태 초기화

def detect_wild_boar(frame):
    results = model.predict(frame, conf=0.7)
    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.model.names[class_id]
                if label == 'wild boar':
                    return True
    return False

def activate_electric_fence():
    global electric_fence_active
    url = 'http://192.168.0.101:8502/detect'
    payload = {'action': 'activate'}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            electric_fence_active = True  # 전기 방벽 활성화
            return True
        else:
            return False
    except Exception as e:
        return False

def deactivate_electric_fence():
    global electric_fence_active
    url = 'http://192.168.0.101:8502/detect'
    payload = {'action': 'deactivate'}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            electric_fence_active = False  # 전기 방벽 비활성화
            return True
        else:
            return False
    except Exception as e:
        return False

st.title("멧돼지 감지 시스템")
st.sidebar.header("설정")

# 비디오 업로드
uploaded_file = st.sidebar.file_uploader("비디오 파일 업로드", type=['mp4', 'avi', 'mov'])

if uploaded_file is not None:
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name

    cap = cv2.VideoCapture(temp_file_path)

    # 비디오 파일 열기 확인
    if not cap.isOpened():
        st.error("비디오 파일을 열 수 없습니다.")
    else:
        frame_interval = 5
        frame_count = 0
        wild_boar_detected = False
        image_path = "detected_boar_image.jpg"  # 감지된 이미지를 저장할 경로

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            if frame_count % frame_interval == 0:
                frame_resized = cv2.resize(frame, (640, 640))
                detected = detect_wild_boar(frame_resized)
                if detected:
                    wild_boar_detected = True
                    cv2.imwrite(image_path, frame_resized)  # 감지된 이미지를 저장
                    st.image(image_path, caption="감지된 멧돼지", use_column_width=True)
                    st.success("멧돼지가 감지되었습니다.")
                    break

        cap.release()
        os.remove(temp_file_path)

    if not wild_boar_detected:
        st.warning("멧돼지가 감지되지 않았습니다.")

# 전기 방벽 조작
if st.sidebar.button("전기 방벽 작동"):
    if activate_electric_fence():
        st.success("전기 방벽이 작동되었습니다.")
    else:
        st.error("전기 방벽 작동 실패.")

if st.sidebar.button("전기 방벽 끄기"):
    if deactivate_electric_fence():
        st.success("전기 방벽이 꺼졌습니다.")
    else:
        st.error("전기 방벽 끄기 실패.")

# 현재 상태 표시
st.sidebar.subheader("현재 상태")
st.sidebar.write(f"전기 방벽 활성화: {electric_fence_active}")

if __name__ == "__main__":
    st.write("애플리케이션이 실행 중입니다.")
