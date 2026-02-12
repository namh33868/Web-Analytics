# utils/updater.py
import requests
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QPushButton, QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal, Qt

class UpdateChecker(QThread):
    """Thread kiểm tra update không block UI"""
    update_available = pyqtSignal(dict)  # {version, download_url, changelog}
    no_update = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, current_version, update_url):
        super().__init__()
        self.current_version = current_version
        self.update_url = update_url
    
    def run(self):
        """Kiểm tra GitHub releases hoặc custom API"""
        try:
            # Method 1: GitHub Releases
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()
            
            latest = response.json()
            
            # Parse version (v1.2.3 -> 1.2.3)
            latest_version = latest['tag_name'].lstrip('v')
            current = self.current_version.lstrip('v')
            
            if self.version_greater(latest_version, current):
                update_info = {
                    'version': latest_version,
                    'download_url': latest['assets'][0]['browser_download_url'] if latest.get('assets') else None,
                    'changelog': latest.get('body', 'No changelog provided'),
                    'release_date': latest.get('published_at', '')
                }
                self.update_available.emit(update_info)
            else:
                self.no_update.emit()
                
        except Exception as e:
            self.error.emit(f"Update check failed: {str(e)}")
    
    def version_greater(self, v1, v2):
        """So sánh phiên bản (1.2.3 > 1.1.5)"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        return v1_parts > v2_parts


class UpdateDownloader(QThread):
    """Thread download update không block UI"""
    progress = pyqtSignal(int)  # 0-100
    finished = pyqtSignal(str)  # file_path
    error = pyqtSignal(str)
    
    def __init__(self, download_url, save_path):
        super().__init__()
        self.download_url = download_url
        self.save_path = save_path
    
    def run(self):
        """Download file với progress tracking"""
        try:
            response = requests.get(self.download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(self.save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress.emit(progress)
            
            self.finished.emit(self.save_path)
            
        except Exception as e:
            self.error.emit(f"Download failed: {str(e)}")


class UpdateDialog(QDialog):
    """Dialog thông báo update đẹp"""
    
    def __init__(self, parent, update_info):
        super().__init__(parent)
        self.update_info = update_info
        self.downloaded_file = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🆕 Update Available")
        self.setFixedSize(550, 400)
        self.setStyleSheet("""
            QDialog { 
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1e293b,stop:1 #334155); 
                color: white; 
            }
            QLabel { color: #e2e8f0; font-size: 14px; }
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #3b82f6,stop:1 #1d4ed8);
                border: none; border-radius: 10px; padding: 14px 28px;
                color: white; font-size: 15px; font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #60a5fa,stop:1 #3b82f6);
            }
            QProgressBar {
                background: rgba(255,255,255,0.1); border: none; border-radius: 8px;
                height: 25px; text-align: center; color: white; font-weight: 600;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #10b981,stop:1 #059669);
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🎉 New Version Available!")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #60a5fa;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version info
        version_label = QLabel(f"<b>Current:</b> v{self.parent().version}<br>"
                               f"<b>Latest:</b> v{self.update_info['version']}")
        version_label.setStyleSheet("background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;")
        layout.addWidget(version_label)
        
        # Changelog
        changelog_label = QLabel("<b>📝 What's New:</b>")
        layout.addWidget(changelog_label)
        
        changelog_text = QLabel(self.update_info['changelog'][:300] + "...")
        changelog_text.setWordWrap(True)
        changelog_text.setStyleSheet("background: rgba(255,255,255,0.03); padding: 15px; border-radius: 10px; font-size: 13px;")
        layout.addWidget(changelog_text)
        
        # Progress bar (ẩn mặc định)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 13px;")
        layout.addWidget(self.status_label)
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)
        
        self.update_btn = QPushButton("🚀 Update Now")
        self.update_btn.clicked.connect(self.start_update)
        btn_layout.addWidget(self.update_btn)
        
        later_btn = QPushButton("⏰ Remind Me Later")
        later_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
            }
            QPushButton:hover { background: rgba(255,255,255,0.15); }
        """)
        later_btn.clicked.connect(self.reject)
        btn_layout.addWidget(later_btn)
        
        layout.addLayout(btn_layout)
    
    def start_update(self):
        """Bắt đầu download update"""
        self.update_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("⏳ Downloading update...")
        
        download_url = self.update_info.get('download_url')
        if not download_url:
            self.status_label.setText("❌ No download URL found")
            return
        
        save_path = Path(os.getcwd()) / f"WebAnalytics_v{self.update_info['version']}.exe"
        
        self.downloader = UpdateDownloader(download_url, str(save_path))
        self.downloader.progress.connect(self.update_progress)
        self.downloader.finished.connect(self.on_download_complete)
        self.downloader.error.connect(self.on_download_error)
        self.downloader.start()
    
    def update_progress(self, percent):
        """Cập nhật progress bar"""
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"⏳ Downloading... {percent}%")
    
    def on_download_complete(self, file_path):
        """Download xong → cài đặt"""
        self.downloaded_file = file_path
        self.status_label.setText("✅ Download complete!")
        self.progress_bar.setValue(100)
        
        # Hiện nút Install
        self.update_btn.setText("🔧 Install & Restart")
        self.update_btn.setEnabled(True)
        self.update_btn.clicked.disconnect()
        self.update_btn.clicked.connect(self.install_update)
    
    def on_download_error(self, error_msg):
        """Download lỗi"""
        self.status_label.setText(f"❌ {error_msg}")
        self.update_btn.setEnabled(True)
        self.update_btn.setText("🔄 Retry")
    
    def install_update(self):
        """Cài update và restart app"""
        if self.downloaded_file and os.path.exists(self.downloaded_file):
            # Backup current exe
            current_exe = sys.executable
            backup = current_exe + ".backup"
            
            try:
                # Windows: Replace exe và restart
                if sys.platform == 'win32':
                    batch_script = f"""
@echo off
timeout /t 2 /nobreak >nul
move /y "{self.downloaded_file}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
                    """
                    batch_file = Path(os.getcwd()) / "update.bat"
                    batch_file.write_text(batch_script)
                    
                    subprocess.Popen(['cmd', '/c', str(batch_file)], 
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    self.status_label.setText("🔄 Restarting app...")
                    QMessageBox.information(self, "Update", 
                        "App will restart in 2 seconds to complete update!")
                    
                    sys.exit(0)  # Close current app
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", 
                    f"Update failed: {e}\n\nManually replace with:\n{self.downloaded_file}")
