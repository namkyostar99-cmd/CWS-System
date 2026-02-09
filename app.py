from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import cv2
import numpy as np
from control_logic import manager

app = Flask(__name__)

# 위반 기록을 저장할 리스트 (메모리 저장 방식)
violation_history = []

# ----------------------------------------------------------------
# [1] 페이지 라우팅 (Multi-Page)
# ----------------------------------------------------------------

@app.route('/')
def index():
    """메인 인덱스 페이지: 로그인 버튼 존재"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지: 버튼 클릭 시 모니터링 페이지로 리다이렉트"""
    if request.method == 'POST':
        # 실제 인증 로직은 생략하고 바로 모니터링 페이지로 이동
        return redirect(url_for('monitoring'))
    return render_template('login.html')

@app.route('/monitoring')
def monitoring():
    """관제 시스템 페이지: 영상 스트리밍, ROI 설정, 로그 출력"""
    return render_template('monitoring.html')

# ----------------------------------------------------------------
# [2] 데이터 통신 API
# ----------------------------------------------------------------

@app.route('/set_roi', methods=['POST'])
def set_roi():
    """프론트엔드에서 클릭한 4개의 좌표를 받아 ROI 설정"""
    data = request.json
    points = data.get('points', [])
    manager.set_roi(points)
    return jsonify({"status": "success", "received": points})

@app.route('/get_status')
def get_status():
    """현재 신호 상태와 위반 로그를 프론트엔드에 전달 (Polling용)"""
    return jsonify({
        "signal": manager.current_signal,
        "logs": violation_history[-20:]  # 최신 20개 로그만 전송
    })

# ----------------------------------------------------------------
# [3] 영상 스트리밍 엔진
# ----------------------------------------------------------------

def gen_frames():
    """카메라 영상을 읽어와 분석 후 프레임 전송"""
    # 0번 카메라이며, 필요 시 동영상 파일 경로로 변경 가능
    cap = cv2.VideoCapture(0) 
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        # control_logic의 manager를 통해 분석 및 시각화 수행
        frame, violations = manager.draw_and_analyze(frame)
        
        # 새로운 위반 사항이 발생하면 리스트에 추가
        if violations:
            violation_history.extend(violations)
            # 메모리 관리를 위해 최근 100개까지만 유지
            if len(violation_history) > 100:
                violation_history.pop(0)

        # 프레임을 JPEG 포맷으로 인코딩하여 전송
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """이미지 태그(<img src="/video_feed">)에 영상을 스트리밍하는 엔드포인트"""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# ----------------------------------------------------------------
# [4] 메인 실행
# ----------------------------------------------------------------

if __name__ == '__main__':
    # debug=True 설정 시 코드 수정 시 자동 재시작
    # 실제 배포 시에는 host='0.0.0.0'으로 설정하여 외부 접속 허용 가능
    app.run(host='0.0.0.0', port=5000, debug=False)