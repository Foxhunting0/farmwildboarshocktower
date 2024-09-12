import streamlit as st
import cv2
import tempfile
import os
import requests
from ultralytics import YOLO
from PIL import Image

# Initialize YOLO model
pt = 'farm.pt'
model = YOLO(pt)

# Electric fence mode and status
automatic_mode = True  # Default to automatic mode
electric_fence_active = False  # Initial electric fence status


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
            electric_fence_active = True
            st.success('전기 방벽이 작동되었습니다.')
            return True
        else:
            st.error(f'전기 방벽 작동 실패: {response.status_code}, {response.text}')
            return False
    except Exception as e:
        st.error(f'오류 발생: {e}')
        return False

def deactivate_electric_fence():
    global electric_fence_active
    url = 'http://192.168.0.101:8502/detect'
    payload = {'action': 'deactivate'}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            electric_fence_active = False
            st.success('전기 방벽이 꺼졌습니다.')
            return True
        else:
            st.error(f'전기 방벽 끄기 실패: {response.status_code}, {response.text}')
            return False
    except Exception as e:
        st.error(f'오류 발생: {e}')
        return False

def process_video(file):
    if not file.name.lower().endswith(('.mp4', '.avi', '.mov')):
        st.error("지원하지 않는 비디오 형식입니다.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    cap = cv2.VideoCapture(temp_file_path)

    if not cap.isOpened():
        st.error("비디오 파일을 열 수 없습니다.")
        return

    frame_interval = 5
    frame_count = 0
    wild_boar_detected = False
    detected_frame = None

    try:
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
                    detected_frame = frame_resized
                    break
    finally:
        cap.release()
        os.remove(temp_file_path)

    if wild_boar_detected and detected_frame is not None:
        st.success("멧돼지가 감지되었습니다.")
        img = cv2.cvtColor(detected_frame, cv2.COLOR_BGR2RGB)
        st.image(img, caption="Detected Wild Boar", use_column_width=True)
    else:
        st.info("멧돼지가 감지되지 않았습니다.")

# Streamlit app layout
st.title("Wild Boar Detection and Electric Fence Control")

# Electric Fence Control
st.header("Electric Fence Control")
fence_status = "On" if electric_fence_active else "Off"
st.write(f"전기 방벽 상태: **{fence_status}**")

col1, col2 = st.columns(2)
with col1:
    if st.button("Activate Electric Fence"):
        activate_electric_fence()
with col2:
    if st.button("Deactivate Electric Fence"):
        deactivate_electric_fence()

# Video Upload and Wild Boar Detection
st.header("Wild Boar Detection")
uploaded_video = st.file_uploader("비디오 업로드", type=["mp4", "avi", "mov"])

if uploaded_video is not None:
    st.write("비디오 파일을 처리 중입니다...")
    process_video(uploaded_video)

# Set mode
st.header("Set Mode")
mode = st.selectbox("모드를 선택하세요", ["automatic", "manual"])

if st.button("Set Mode"):
    if mode == "automatic":
        automatic_mode = True
        st.write("모드가 'automatic'으로 설정되었습니다.")
    else:
        automatic_mode = False
        deactivate_electric_fence()
        st.write("모드가 'manual'로 설정되었습니다.")
