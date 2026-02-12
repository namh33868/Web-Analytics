# core/analytics.py
import pandas as pd
import numpy as np
from typing import Dict, List

class AnalyticsEngine:
    @staticmethod
    def calculate_stats(df: pd.DataFrame) -> Dict:
        """Tính toán các thống kê tổng hợp"""
        stats = {
            'total_pages': len(df),
            'avg_word_count': df['word_count'].mean(),
            'total_internal_links': df['internal_links'].sum(),
            'total_external_links': df['external_links'].sum(),
            'top_pages_by_words': df.nlargest(5, 'word_count')[['url', 'word_count']].to_dict('records'),
        }
        return stats

    @staticmethod
    def get_trends(df: pd.DataFrame) -> Dict:
        """Phân tích xu hướng theo thời gian"""
        df['crawl_time'] = pd.to_datetime(df['crawl_time'])
        daily_stats = df.groupby(df['crawl_time'].dt.date).agg({
            'word_count': 'mean',
            'img_count': 'mean'
        }).reset_index()
        return daily_stats.to_dict('records')
