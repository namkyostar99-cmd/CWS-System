import random
import time

class DummyTrafficModel:
    def __init__(self):
        # 현재 화면에 있는 차량들 관리 {track_id: [x1, y1, x2, y2, speed]}
        self.vehicles = {}
        self.next_id = 101  # 다음에 부여할 신규 ID
        self.signal_status = "RED"
        self.last_signal_change = time.time()
        self.last_spawn_time = 0 # 마지막 차량 생성 시간

    def get_inference(self, frame):
        h, w, _ = frame.shape
        results = []

        # 1. 신호등 상태 업데이트 (10초 주기)
        if time.time() - self.last_signal_change > 10:
            self.signal_status = "RED" if self.signal_status == "GREEN" else "GREEN"
            self.last_signal_change = time.time()

        # 2. 새로운 차량 생성 (약 2초마다 새로운 ID 부여)
        if time.time() - self.last_spawn_time > 2.0:
            new_id = self.next_id
            x_start = random.randint(100, w - 150)
            # [x1, y1, x2, y2, speed]
            self.vehicles[new_id] = [x_start, -50, x_start + 60, 10, random.randint(5, 12)]
            self.next_id += 1  # ID 증가
            self.last_spawn_time = time.time()

        # 3. 기존 차량 이동 및 결과 리스트 생성
        active_vehicles = {}
        for vid, data in self.vehicles.items():
            data[1] += data[4]  # y1 이동
            data[3] += data[4]  # y2 이동

            # 화면 안에 있는 경우만 유지
            if data[1] < h:
                active_vehicles[vid] = data
                results.append({
                    "track_id": vid,
                    "label": "car",
                    "bbox": [data[0], data[1], data[2], data[3]],
                    "conf": 0.9
                })
        
        self.vehicles = active_vehicles # 화면 밖 차량 자동 삭제

        # 4. 신호등 데이터 추가
        results.append({
            "track_id": 999,
            "label": "traffic_light",
            "status": self.signal_status,
            "bbox": [20, 20, 70, 120],
            "conf": 0.99
        })

        return results