import sqlite3

def init_db():
    """데이터베이스 테이블 초기화"""
    conn = sqlite3.connect('traffic_system.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS violations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  track_id INTEGER, 
                  timestamp TEXT, 
                  filename TEXT, 
                  url TEXT)''')
    conn.commit()
    conn.close()

def save_violation_to_db(track_id, timestamp, filename, url):
    """위반 내역 및 접근 URL 저장"""
    conn = sqlite3.connect('traffic_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO violations (track_id, timestamp, filename, url) VALUES (?, ?, ?, ?)",
              (track_id, timestamp, filename, url))
    conn.commit()
    conn.close()