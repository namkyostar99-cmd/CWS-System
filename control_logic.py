import cv2
import numpy as np
import os
from datetime import datetime
from yolo_dummy import DummyTrafficModel
from database import save_violation_to_db

class TrafficManager:
    def __init__(self):
        self.model = DummyTrafficModel()
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
        predictions = self.model.get_inference(frame)
        self.current_signal = "GREEN"
        violations = []
        current_ids = [p['track_id'] for p in predictions]

        for pred in predictions:
            if pred['label'] == 'traffic_light':
                self.current_signal = pred['status']

        for pred in predictions:
            if pred['label'] != 'car': continue
            x1, y1, x2, y2 = map(int, pred['bbox'])
            tid = pred['track_id']
            cx, cy = (x1 + x2) // 2, y2 

            is_inside = False
            if len(self.roi_points) >= 3:
                is_inside = cv2.pointPolygonTest(self.roi_points, (float(cx), float(cy)), False) >= 0

            if self.current_signal == "RED" and is_inside and tid not in self.violated_ids:
                now = datetime.now()
                timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')
                file_name = f"violation_{tid}_{now.strftime('%H%M%S')}.jpg"
                cv2.imwrite(os.path.join(self.save_folder, file_name), frame)
                
                v_url = f"/violation/{file_name}"
                save_violation_to_db(tid, timestamp_str, file_name, v_url)
                
                # 새로운 프론트엔드 사이드바 '위반 내역'에 들어갈 태그 생성
                log_entry = f"[{now.strftime('%H:%M:%S')}] ID {tid} 위반 <a href='{v_url}' target='_blank' style='color:#ff6b6b; margin-left:5px;'>[보기]</a>"
                violations.append(log_entry)
                self.violated_ids.add(tid)
            
            color = (0, 0, 255) if tid in self.violated_ids else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        if len(self.roi_points) >= 3:
            l_color = (0, 0, 255) if self.current_signal == "RED" else (0, 255, 0)
            cv2.polylines(frame, [self.roi_points], True, l_color, 2)

        self.violated_ids = {tid for tid in self.violated_ids if tid in current_ids}
        return frame, violations

manager = TrafficManager()