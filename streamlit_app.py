import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."


from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np
import requests
import matplotlib.pyplot as plt

app = Flask(__name__)

pt = 'farm.pt'  # 모델 파일 경로
model = YOLO(pt)  # YOLO 모델 로드

def detect_wild_boar(frame):
    results = model.predict(frame, conf=0.7)
    for result in results:
        if result.boxes is not None and len(result.boxes) > 0:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.model.names[class_id]
                if label == 'wild boar':
                    return True, result
    return False, None

def activate_electric_fence():
    url = '192.168.0.75 :5000'  # 전기 방벽 제어 URL
    payload = {'action': 'activate'}
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print('오류 발생:', e)
        return False

@app.route('/detect', methods=['POST'])
def detect():
    video_path = request.json.get('video_path')
    cap = cv2.VideoCapture(video_path)
    confirm = []
    frame_interval = 5
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if frame_count % frame_interval == 0:
            frame_resized = cv2.resize(frame, (640, 640))
            detected, result = detect_wild_boar(frame_resized)
            if detected:
                if activate_electric_fence():
                    confirm.append(result)

    
    cap.release()

    if confirm:
        return jsonify({"status": "success", "detected": True, "data": str(confirm)})
    else:
        return jsonify({"status": "success", "detected": False, "message": "감지된 멧돼지가 없습니다."})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # 서버 실행

    
)
