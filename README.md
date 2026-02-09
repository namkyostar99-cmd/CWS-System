# CWS-System (Child-zone Violation Watch System)
>어린이 보호구역 내 실시간 교통 법규 위반을 감지하고 관리하는 스마트 관제 시스템입니다. 인공지능 객체 인식과 웹 기반 모니터링을 결합하여 안전한 통학로 환경을 구축하는 것을 목표로 합니다.

# 주요 기능
>실시간 모니터링: Flask를 활용한 고해상도 실시간 영상 스트리밍.

>4점 클릭 ROI 설정: 관리자가 영상 화면을 직접 클릭하여 임계구역(감지 영역)을 자유롭게 설정.

>위반 자동 감지: 지정된 구역 내에서 적색 신호 시 차량 진입을 AI로 판별.

# Tech Stack
>Backend: Python, Flask

>Computer Vision: OpenCV, NumPy

>Frontend: HTML5, CSS3 (Bootstrap 5), JavaScript (Vanilla JS)

# 프로젝트 구조

```
CWS-System/
├── app.py              # Flask 메인 서버 및 라우팅
├── control_logic.py    # ROI 판별 및 영상 처리 엔진
├── yolo_dummy.py       # 객체 인식 시뮬레이션 모델
└── templates/
    ├── index.html      # 메인 진입 페이지
    ├── login.html      # 로그인 페이지
    ├── monitoring.html # 실시간 관제 대시보드
```    

# 시작하기
>환경 설정
Python 3.8 이상이 필요합니다. 필요한 라이브러리를 설치합니다.

# Bash
>pip install flask opencv-python numpy
- 서버 실행
# Bash
>python app.py
- 시스템 접속

>브라우저를 열고 아래 주소로 접속하세요.
- URL: http://localhost:5000
>로그인 후 관제 시스템 페이지에서 화면을 4번 클릭하여 ROI를 설정하세요.

# 참고 사항
>현재 테스트를 위해 yolo_dummy.py를 통해 가상 차량 데이터를 생성 중입니다.

>실제 환경 적용 시 control_logic.py 내의 cv2.VideoCapture(0) 설정을 카메라 IP 주소나 RTSP 경로로 수정해야 합니다.
