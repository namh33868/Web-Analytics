# gui/main_window.py - IMPORT QtWebEngine ĐẦU TIÊN
from PyQt6.QtWebEngineWidgets import QWebEngineView  # IMPORT NGAY DÒNG 1

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from datetime import datetime
from core.scraper import WebScraper
from core.db_manager import DatabaseManager
from gui.charts import ChartGenerator
from utils.updater import UpdateChecker, UpdateDialog

class ScrapeWorker(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        self.progress.emit("Fetching " + self.url)
        scraper = WebScraper()
        data = scraper.analyze_single_page(self.url)
        self.progress.emit("Done!")
        if 'error' not in data:
            db = DatabaseManager()
            db.save_page_data(data)
            db.close()
        self.finished.emit(data)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "1.0.0"  # VERSION HIỆN TẠI
        self.update_url = "https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/releases/latest"

        self.db = DatabaseManager()
        self.init_ui()
        self.refresh_all()

        # CHECK UPDATE KHI KHỞI ĐỘNG (sau 2 giây)
        QTimer.singleShot(2000, self.check_for_updates)

    def init_ui(self):
        self.setWindowTitle("Web Analytics Dashboard")
        self.setGeometry(100, 100, 1400, 850)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left sidebar - Controls
        left_panel = QFrame()
        left_panel.setFixedWidth(380)
        left_panel.setStyleSheet("""
            QFrame { 
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #1e293b,stop:1 #334155); 
                border-radius: 15px; border: 1px solid #475569;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("🌐 Web Analytics")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #60a5fa; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title)
        
        # URL Input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.setStyleSheet("""
            QLineEdit { 
                padding: 15px; border: 2px solid #475569; border-radius: 10px; 
                background: #0f172a; color: white; font-size: 14px; 
            }
            QLineEdit:focus { border-color: #60a5fa; }
        """)
        left_layout.addWidget(self.url_input)
        
        # Buttons - FIX: Tăng size + margin
        self.scrape_btn = QPushButton("🚀 Analyze Page")
        self.scrape_btn.clicked.connect(self.start_scrape)
        self.scrape_btn.setMinimumHeight(50)
        self.scrape_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #3b82f6,stop:1 #1d4ed8); 
                border: none; border-radius: 10px; color: white; font-size: 16px; font-weight: 600; padding: 15px;
            }
            QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #60a5fa,stop:1 #3b82f6); }
            QPushButton:pressed { background: #1d4ed8; }
        """)
        left_layout.addWidget(self.scrape_btn)
        
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.clicked.connect(self.refresh_all)
        self.refresh_btn.setMinimumHeight(50)
        self.refresh_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #10b981,stop:1 #059669); 
                border: none; border-radius: 10px; color: white; font-size: 16px; font-weight: 600; padding: 15px;
            }
            QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #34d399,stop:1 #10b981); }
        """)
        left_layout.addWidget(self.refresh_btn)

        # Nút Check Update
        self.update_btn = QPushButton("🔄 Check Updates")
        self.update_btn.clicked.connect(self.check_for_updates)
        self.update_btn.setMinimumHeight(44)
        self.update_btn.setStyleSheet("""
            QPushButton {
                background: rgba(139,92,246,0.8); border-radius: 10px;
                padding: 12px; color: white; font-weight: 600;
            }
            QPushButton:hover { background: rgba(167,139,250,0.9); }
        """)
        left_layout.addWidget(self.update_btn)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #94a3b8; font-size: 12px; margin-top: 20px;")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        
        layout.addWidget(left_panel)
        
        # Right main content
        right_panel = QFrame()
        right_panel.setStyleSheet("background: rgba(15,23,42,0.9); border-radius: 15px; border: 1px solid #334155;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(25, 25, 25, 25)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #334155; background: rgba(30,41,59,0.8); border-radius: 12px; 
            }
            QTabBar::tab { 
                background: rgba(71,85,105,0.7); color: #cbd5e1; padding: 15px 30px; 
                margin-right: 4px; border-radius: 8px 8px 0 0; font-weight: 500;
            }
            QTabBar::tab:selected { 
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #3b82f6,stop:1 #1e40af); 
                color: white; 
            }
        """)
        
        # Data Table Tab
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("""
            QTableWidget { 
                background: rgba(255,255,255,0.05); border-radius: 8px; 
                gridline-color: rgba(148,163,184,0.3); alternate-background-color: rgba(255,255,255,0.02);
            }
            QTableWidget::item { padding: 12px; color: #e2e8f0; }
            QTableWidget::item:selected { background: rgba(59,130,246,0.5); color: white; }
        """)
        self.tabs.addTab(self.data_table, "📋 Data")
        
        # Charts Tab  
        self.chart_view = QWebEngineView()
        self.tabs.addTab(self.chart_view, "📈 Analytics")
        
        right_layout.addWidget(self.tabs)
        layout.addWidget(right_panel, 1)
        
        layout.setStretch(1, 3)  # Right panel lớn hơn

    def start_scrape(self):
        """FIX: Button click handler"""
        print("BUTTON CLICKED!")  # Debug log
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("❌ Enter a URL!")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        self.status_label.setText("⏳ Scraping...")
        self.scrape_btn.setEnabled(False)  # Prevent spam click
        
        self.scrape_worker = ScrapeWorker(url)
        self.scrape_worker.progress.connect(self.update_status)
        self.scrape_worker.finished.connect(self.on_scrape_complete)
        self.scrape_worker.start()

    def update_status(self, message):
        self.status_label.setText(message)

    def on_scrape_complete(self, data):
        self.scrape_btn.setEnabled(True)
        self.status_label.setText("✅ Complete!")
        self.refresh_all()

    def refresh_all(self):
        df = self.db.get_all_data()
        print(f"Refreshing {len(df)} rows")  # Debug
        
        # Table
        self.data_table.setRowCount(len(df))
        if len(df) > 0:
            self.data_table.setColumnCount(len(df.columns))
            self.data_table.setHorizontalHeaderLabels(df.columns)
            for i, (_, row) in enumerate(df.iterrows()):
                for j, val in enumerate(row):
                    self.data_table.setItem(i, j, QTableWidgetItem(str(val)))
        
        # Charts
        html = ChartGenerator.create_dashboard_charts(df)
        self.chart_view.setHtml(html)
        
        self.status_label.setText(f"📊 {len(df)} pages analyzed")

    def closeEvent(self, event):
        self.db.close()
        event.accept()

    # ===== AUTO-UPDATE =====
    def check_for_updates(self):
        """Kiểm tra update từ GitHub"""
        if hasattr(self, "update_btn"):
            self.update_btn.setText("⏳ Checking...")
            self.update_btn.setEnabled(False)

        self.update_checker = UpdateChecker(self.version, self.update_url)
        self.update_checker.update_available.connect(self.show_update_dialog)
        self.update_checker.no_update.connect(self.on_no_update)
        self.update_checker.error.connect(self.on_update_error)
        self.update_checker.start()

    def show_update_dialog(self, update_info):
        """Hiện dialog update"""
        if hasattr(self, "update_btn"):
            self.update_btn.setText("🔄 Check Updates")
            self.update_btn.setEnabled(True)

        dialog = UpdateDialog(self, update_info)
        dialog.exec()

    def on_no_update(self):
        """Đã là phiên bản mới nhất"""
        if hasattr(self, "update_btn"):
            self.update_btn.setText("✅ Up to date")
            self.update_btn.setEnabled(True)
            QTimer.singleShot(3000, lambda: self.update_btn.setText("🔄 Check Updates"))

    def on_update_error(self, error_msg):
        """Lỗi khi check update"""
        if hasattr(self, "update_btn"):
            self.update_btn.setText("❌ Check Failed")
            self.update_btn.setEnabled(True)
        print(f"Update check error: {error_msg}")
