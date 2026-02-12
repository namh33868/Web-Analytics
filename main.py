# main.py - WITH AUTO ERROR HANDLING
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# IMPORT AUTO-FIX FIRST
from utils.error_handler import error_fixer  # Auto-fix enabled

from gui.main_window import MainWindow

if __name__ == "__main__":
    try:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("📝 Check logs/ folder for details")
