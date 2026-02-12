# utils/error_handler.py
import sys
import traceback
import logging
from datetime import datetime

class AutoErrorFixer:
    """Hệ thống tự động phát hiện và sửa lỗi"""
    
    def __init__(self):
        self.log_file = f"logs/errors_{datetime.now().strftime('%Y%m%d')}.log"
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging system"""
        import os
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            filename=self.log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Global exception handler với auto-fix"""
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logging.error(f"CRASH:\n{error_msg}")
        
        # Auto-fix patterns
        fixes = {
            'ImportError': self.fix_import_error,
            'ModuleNotFoundError': self.fix_missing_module,
            'AttributeError': self.fix_attribute_error,
            'DatabaseError': self.fix_database_error,
        }
        
        for error_type, fix_func in fixes.items():
            if error_type in str(exc_type):
                fix_func(exc_value, error_msg)
                return
        
        print(f"\n❌ CRITICAL ERROR:\n{error_msg}")
        print(f"📝 Log saved: {self.log_file}")
    
    def fix_import_error(self, error, traceback):
        """Tự động cài package thiếu"""
        print(f"\n🔧 AUTO-FIX: Import error detected")
        
        # Extract missing module
        import re
        match = re.search(r"No module named ['\"]([^'\"]+)['\"]", str(error))
        if match:
            module = match.group(1)
            print(f"📦 Installing missing: {module}")
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                print(f"✅ {module} installed! Please restart app.")
            except:
                print(f"❌ Auto-install failed. Run: pip install {module}")
    
    def fix_missing_module(self, error, traceback):
        """Alias cho fix_import_error"""
        self.fix_import_error(error, traceback)
    
    def fix_attribute_error(self, error, traceback):
        """Suggest fixes cho attribute errors"""
        print(f"\n🔧 AUTO-FIX: Attribute error")
        if 'QWebEngineView' in str(error):
            print("💡 FIX: Add to main.py BEFORE QApplication:")
            print("   from PyQt6.QtCore import Qt")
            print("   QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)")
    
    def fix_database_error(self, error, traceback):
        """Reset corrupted database"""
        print(f"\n🔧 AUTO-FIX: Database error detected")
        print("🗑️ Backing up and resetting database...")
        import os
        import shutil
        from utils.config import DB_PATH
        
        if os.path.exists(DB_PATH):
            backup = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(DB_PATH, backup)
            os.remove(DB_PATH)
            print(f"✅ Database reset. Backup: {backup}")
            print("🔄 Please restart app.")

# Global error handler setup
error_fixer = AutoErrorFixer()
sys.excepthook = error_fixer.handle_exception
