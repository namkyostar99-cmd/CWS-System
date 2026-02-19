import cv2
import numpy as np
import os
from datetime import datetime
from ultralytics import YOLO  # 실제 YOLO 추론을 위해 추가
from database import save_violation_to_db

class TrafficManager:
    def __init__(self):
        # YOLO26n 모델 로드 (파일이 없을 경우 자동 다운로드 시도 또는 경로 지정 필요)
        try:
            self.model = YOLO('best.pt') 
        except:
            # 모델 파일명이 다를 경우를 대비해 기본 모델로 예외 처리 가능
            self.model = YOLO('best.pt') 
            
        self.roi_points = [] 
        self.violated_ids = set()
        self.current_signal = "RED" # 초기값 RED 설정
        self.save_folder = "static/violations/"
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

    def set_roi(self, points):
        """script.js에서 보낸 [{px, py}, ...] 형식을 넘파이 배열로 변환"""
        if len(points) >= 3:
            self.roi_points = np.array([[p['px'], p['py']] for p in points], dtype=np.int32)

    def draw_and_analyze(self, frame):
        # 실제 YOLO26n 추론 수행 (persist=True로 객체 추적 활성화)
        
        results = self.model.track(frame, imgsz=1280, conf=0.22, persist=True, verbose=False)
        
        # 기본 신호 상태 초기화 (탐지되지 않을 경우의 기본값)
        # 기존 로직 유지: traffic_light 탐지 시 업데이트
        violations = []
        
        # YOLO 결과에서 바운딩 박스 및 트래킹 ID 추출
        current_ids = []
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            clss = results[0].boxes.cls.cpu().numpy().astype(int)
            names = self.model.names
            current_ids = ids.tolist()

            # 1. 먼저 신호등 상태 확인 (기존 로직 순서 유지)
            for box, cls in zip(boxes, clss):
                label = names[cls]
                if label == 'traffic_light':
                    # 실제 환경에서는 신호등 색상 분류 로직이 필요하나, 
                    # 기존 구조 유지를 위해 임시로 RED/GREEN 판별 로직(가정) 적용
                    # 여기서는 간단히 탐지 시 현재 신호를 유지하거나 특정 로직 부여
                    pass 

            # 2. 차량 위반 판별
            for box, tid, cls in zip(boxes, ids, clss):
                label = names[cls]
                
                # 'car', 'truck', 'bus' 등 차량 관련 클래스 필터링
                if label not in ['car', 'truck', 'bus']: 
                    continue
                
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) // 2, y2 

                is_inside = False
                if len(self.roi_points) >= 3:
                    is_inside = cv2.pointPolygonTest(self.roi_points, (float(cx), float(cy)), False) >= 0

                # 위반 판단: 빨간불 + ROI 진입 + 미기록 ID
                if self.current_signal == "RED" and is_inside and tid not in self.violated_ids:
                    now = datetime.now()
                    timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')
                    file_name = f"violation_{tid}_{now.strftime('%H%M%S')}.jpg"
                    cv2.imwrite(os.path.join(self.save_folder, file_name), frame)
                    
                    v_url = f"/violation/{file_name}"
                    save_violation_to_db(tid, timestamp_str, file_name, v_url)
                    
                    log_entry = f"[{now.strftime('%H:%M:%S')}] ID {tid} 위반 <a href='{v_url}' target='_blank' style='color:#ff6b6b; margin-left:5px;'>[보기]</a>"
                    violations.append(log_entry)
                    self.violated_ids.add(tid)
                
                # 박스 그리기
                color = (0, 0, 255) if tid in self.violated_ids else (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"ID: {tid} {label}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # ROI 영역 시각화
        if len(self.roi_points) >= 3:
            l_color = (0, 0, 255) if self.current_signal == "RED" else (0, 255, 0)
            cv2.polylines(frame, [self.roi_points], True, l_color, 2)

        # 트래킹 종료된 ID 정리
        self.violated_ids = {tid for tid in self.violated_ids if tid in current_ids}
        
        return frame, violations

manager = TrafficManager()