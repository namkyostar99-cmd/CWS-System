import cv2
import numpy as np
from datetime import datetime
from yolo_dummy import DummyTrafficModel

class TrafficManager:
    def __init__(self):
        self.model = DummyTrafficModel()
        # 4개의 좌표 (기본값: 사각형 형태)
        self.roi_points = [] 
        self.violated_ids = set()
        self.prev_y_coords = {}
        self.current_signal = "GREEN"

    def set_roi(self, points):
        """JavaScript로부터 받은 4개의 좌표를 업데이트"""
        if len(points) == 4:
            self.roi_points = np.array(points, dtype=np.int32)

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
            cx, cy = (x1 + x2) // 2, y2 # 차량 하단 중앙점

            # --- 다각형 ROI 내부 판별 ---
            is_inside = False
            if len(self.roi_points) == 4:
                # 점이 다각형 내부에 있는지 검사 (1: 내부, 0: 경계, -1: 외부)
                dist = cv2.pointPolygonTest(self.roi_points, (float(cx), float(cy)), False)
                is_inside = dist >= 0

            if self.current_signal == "RED" and is_inside:
                if tid not in self.violated_ids:
                    violations.append(f"[{datetime.now().strftime('%H:%M:%S')}] ID {tid} 구역 위반!")
                    self.violated_ids.add(tid)
            
            color = (0, 0, 255) if tid in self.violated_ids else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"ID:{tid}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # --- ROI 시각화 ---
        if len(self.roi_points) == 4:
            line_color = (0, 0, 255) if self.current_signal == "RED" else (0, 255, 0)
            cv2.polylines(frame, [self.roi_points], isClosed=True, color=line_color, thickness=2)
            for pt in self.roi_points:
                cv2.circle(frame, tuple(pt), 5, (255, 0, 0), -1)

        self.violated_ids = {tid for tid in self.violated_ids if tid in current_ids}
        return frame, violations

manager = TrafficManager()