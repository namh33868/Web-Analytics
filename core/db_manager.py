# core/db_manager.py
import sqlite3
import pandas as pd
from datetime import datetime
from utils.config import DB_PATH

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.init_db()

    def init_db(self):
        """Tạo bảng nếu chưa có"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                word_count INTEGER,
                img_count INTEGER,
                internal_links INTEGER,
                external_links INTEGER,
                crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def save_page_data(self, data: dict):
        """Lưu dữ liệu 1 trang web"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO pages (url, title, word_count, img_count, 
            internal_links, external_links)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['url'], data['title'], data['word_count'], 
              data['img_count'], data['internal_links'], data['external_links']))
        self.conn.commit()

    def get_all_data(self) -> pd.DataFrame:
        """Lấy tất cả dữ liệu dạng DataFrame"""
        return pd.read_sql_query("SELECT * FROM pages ORDER BY crawl_time DESC", self.conn)

    def close(self):
        """Đóng kết nối"""
        self.conn.close()
