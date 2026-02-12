# utils/health_check.py
import requests
import json
from datetime import datetime

class HealthMonitor:
    """Monitor app health + auto-update check"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.update_url = "https://api.github.com/repos/yourname/repo/releases/latest"
    
    def check_for_updates(self):
        """Check GitHub releases for updates"""
        try:
            resp = requests.get(self.update_url, timeout=5)
            latest = resp.json()['tag_name']
            
            if latest > self.version:
                print(f"🆕 Update available: {latest}")
                print(f"   Current: {self.version}")
                return latest
            else:
                print(f"✅ Up to date: {self.version}")
        except:
            pass
        return None
    
    def send_crash_report(self, error_log):
        """Gửi crash report lên server (optional)"""
        # Implement webhook to Discord/Telegram
        pass
