from flask import Flask, request, jsonify, send_from_directory
import cv2
import tempfile
import os
import requests
from ultralytics import YOLO

app = Flask(__name__)
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
    url = 'http://192.168.0.75:8502/detect'
    payload = {'action': 'activate'}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            electric_fence_active = True  # 전기 방벽 활성화
            print('전기 방벽이 작동되었습니다.')
            return True
        else:
            print('전기 방벽 작동 실패:', response.status_code, response.text)
            return False
    except Exception as e:
        print('오류 발생:', e)
        return False

def deactivate_electric_fence():
    global electric_fence_active
    url = 'http://192.168.0.75:8502/detect'
    payload = {'action': 'deactivate'}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            electric_fence_active = False  # 전기 방벽 비활성화
            print('전기 방벽이 꺼졌습니다.')
            return True
        else:
            print('전기 방벽 끄기 실패:', response.status_code, response.text)
            return False
    except Exception as e:
        print('오류 발생:', e)
        return False

@app.route('/detect', methods=['POST'])
def detect():
    if 'video' not in request.files:
        return jsonify({"error": "비디오 파일이 필요합니다."}), 400

    file = request.files['video']

    # 비디오 파일 형식 확인
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov')):
        return jsonify({"error": "지원하지 않는 비디오 형식입니다."}), 415

    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        file.save(temp_file.name)
        temp_file_path = temp_file.name

    cap = cv2.VideoCapture(temp_file_path)

    # 비디오 파일 열기 확인
    if not cap.isOpened():
        return jsonify({"error": "비디오 파일을 열 수 없습니다."}), 400

    frame_interval = 5
    frame_count = 0
    wild_boar_detected = False
    image_path = "detected_boar_image.jpg"  # 감지된 이미지를 저장할 경로

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
                    print("멧돼지 감지됨.")

                    # 감지된 멧돼지 이미지 저장
                    cv2.imwrite(image_path, frame_resized)  # 감지된 이미지를 저장
                    return jsonify({"detected": True, "message": "멧돼지가 감지되었습니다.", "image_url": image_path}), 200

    finally:
        cap.release()
        os.remove(temp_file_path)

    if wild_boar_detected:
        return jsonify({"detected": True, "message": "멧돼지가 감지되었습니다."}), 200
    else:
        return jsonify({"detected": False, "message": "멧돼지가 감지되지 않았습니다."}), 200

@app.route('/activate_fence', methods=['POST'])
def activate_fence():
    if activate_electric_fence():
        return jsonify({"message": "전기 방벽이 작동되었습니다."}), 200
    else:
        return jsonify({"error": "전기 방벽 작동 실패."}), 500

@app.route('/fence/<status>', methods=['POST'])
def set_fence(status):
    global fence_state
    if status not in ['on', 'off']:
        return jsonify({"error": "Invalid status"}), 400

    fence_state = (status == 'on')
    return jsonify({"fence_state": fence_state}), 200


@app.route('/fence_image')
def fence_image():
    # 로컬 파일 경로에서 이미지 제공
    return send_from_directory('C:\\Users\\KDP007\\Desktop', '전기방벽.jpg')


@app.route('/set_mode', methods=['POST'])
def set_mode():
    global automatic_mode
    mode = request.json.get('mode')
    if mode not in ['automatic', 'manual']:
        return jsonify({"error": "모드는 'automatic' 또는 'manual'이어야 합니다."}), 400

    automatic_mode = (mode == 'automatic')
    if not automatic_mode:  # 수동 모드일 경우 전기 방벽 비활성화
        deactivate_electric_fence()
    return jsonify({"message": f"모드가 '{mode}'로 설정되었습니다."}), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"electric_fence_active": electric_fence_active}), 200

@app.route('/<path:filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory(os.getcwd(), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501, debug=True)
