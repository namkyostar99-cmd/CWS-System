import os
import mimetypes
import cv2
from flask import Flask, render_template, Response, request, jsonify, send_from_directory
from control_logic import manager
from database import init_db

# 브라우저가 CSS를 텍스트로 오해하지 않도록 MIME 타입 수동 등록
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

# Flask 앱 인스턴스 생성 (static_url_path를 비워 루트 접근성 향상)
app = Flask(__name__, static_url_path='')

# 데이터베이스 및 저장 폴더 초기화
init_db()
VIOLATION_DIR = os.path.join('static', 'violations')
if not os.path.exists(VIOLATION_DIR):
    os.makedirs(VIOLATION_DIR)

# 서버 사이드 실시간 로그 저장소
violation_logs = []

@app.after_request
def add_header(response):
    """모든 응답에 대해 CSS/JS MIME 타입을 강제로 지정하여 적용 오류 방지"""
    if request.path.endswith('.css'):
        response.headers['Content-Type'] = 'text/css'
    elif request.path.endswith('.js'):
        response.headers['Content-Type'] = 'application/javascript'
    return response

# --- [페이지 라우팅 영역] ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/monitoring.html')
def monitoring_page():
    return render_template('monitoring.html')

@app.route('/violation/<filename>')
def violation_detail(filename):
    return render_template('violation_detail.html', filename=filename)

# --- [기능 API 및 영상 스트리밍 영역] ---

@app.route('/video_feed')
def video_feed():
    """YOLO 분석 결과가 시각화된 실시간 영상을 전송"""
    def gen():
        cap = cv2.VideoCapture("http://210.99.70.120:1935/live/cctv006.stream/playlist.m3u8")  # 웹캠 활성화
        while True:
            success, frame = cap.read()
            if not success:
                break
            
            # 제어 로직을 통해 ROI 판별 및 프레임 갱신
            frame, new_violations = manager.draw_and_analyze(frame)
            
            # 발생한 위반 내역을 전역 로그에 추가
            if new_violations:
                violation_logs.extend(new_violations)
            
            # 영상을 JPG로 인코딩하여 스트리밍
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        cap.release()
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_status')
def get_status():
    """프론트엔드 대시보드 업데이트용 신호/로그 데이터 전송"""
    return jsonify({
        "signal": manager.current_signal,
        "logs": violation_logs[-15:] # 최신 15개만
    })

@app.route('/set_roi', methods=['POST'])
def set_roi():
    """관리자가 설정한 ROI 픽셀 좌표를 서버로 전송받아 적용"""
    data = request.json
    points = data.get('points', [])
    manager.set_roi(points)
    print(f"[*] 서버 메시지: ROI 수신 및 적용 완료 ({len(points)} points)")
    return jsonify({"status": "success"})

# --- [경로 예외 처리 영역] ---

@app.route('/static/<path:path>')
def send_static(path):
    """static 폴더 내 리소스 수동 서빙"""
    return send_from_directory('static', path)

@app.route('/<path:filename>')
def serve_fallback(filename):
    """정적 파일 요청이 루트(/)로 들어올 경우 static 폴더에서 찾아 응답"""
    if filename.endswith(('.css', '.js', '.png', '.jpg', '.ico')):
        return send_from_directory('static', filename)
    if filename.endswith('.html'):
        return render_template(filename)
    return render_template('index.html')

if __name__ == '__main__':
    # 5000번 포트에서 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=False)