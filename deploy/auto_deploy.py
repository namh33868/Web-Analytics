# deploy/auto_deploy.py
import os
import subprocess
import sys
from pathlib import Path

class AutoDeployer:
    """Tự động build, test và deploy app"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.dist_folder = self.project_root / "dist"
        
    def check_dependencies(self):
        """Kiểm tra và cài dependencies"""
        print("📦 Checking dependencies...")
        # Map package names -> module names để import kiểm tra
        requirements = {
            'PyQt6': 'PyQt6',
            'PyQt6-WebEngine': 'PyQt6.QtWebEngineWidgets',
            'requests': 'requests',
            'beautifulsoup4': 'bs4',
            'pandas': 'pandas',
            'plotly': 'plotly',
            'pyinstaller': 'PyInstaller',
        }

        for pkg, module_name in requirements.items():
            try:
                __import__(module_name)
                print(f"  ✅ {pkg}")
            except ImportError:
                print(f"  ⚠️ Installing {pkg}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                    print(f"  ✅ Installed {pkg}")
                except Exception as e:
                    print(f"  ❌ Failed to install {pkg}: {e}")
                    return False

        return True
    
    def run_tests(self):
        """Chạy basic tests"""
        print("\n🧪 Running tests...")
        
        # Đảm bảo project_root nằm trong sys.path để import được "gui", "core"
        project_str = str(self.project_root)
        if project_str not in sys.path:
            sys.path.insert(0, project_str)
        
        # Test 1: Import modules
        try:
            from gui.main_window import MainWindow
            from core.scraper import WebScraper
            from core.db_manager import DatabaseManager
            print("  ✅ All modules importable")
        except Exception as e:
            print(f"  ❌ Import test failed: {e}")
            return False
        
        # Test 2: Database connection
        try:
            db = DatabaseManager()
            db.close()
            print("  ✅ Database connection OK")
        except Exception as e:
            print(f"  ❌ Database test failed: {e}")
            return False
        
        # Test 3: Scraper basic
        try:
            scraper = WebScraper()
            data = scraper.analyze_single_page('https://example.com')
            if 'url' in data:
                print("  ✅ Scraper working")
            else:
                print("  ⚠️ Scraper returned incomplete data")
        except Exception as e:
            print(f"  ⚠️ Scraper test failed: {e}")
        
        return True
    
    def build_exe(self):
        """Build standalone EXE"""
        print("\n🔨 Building EXE with PyInstaller...")
        
        # PyInstaller command
        cmd = [
            sys.executable,
            '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', 'WebAnalytics',
            '--add-data', 'data;data',
            'main.py'
        ]

        # Chỉ thêm cờ --icon khi file icon tồn tại, tránh lỗi "expected one argument"
        icon_path = self.project_root / 'assets' / 'icon.ico'
        if icon_path.exists():
            cmd.extend(['--icon', str(icon_path)])
        
        try:
            subprocess.check_call(cmd, cwd=self.project_root)
            print("✅ Build successful!")
            print(f"📦 EXE location: {self.dist_folder / 'WebAnalytics.exe'}")
            return True
        except Exception as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def deploy_local(self):
        """Copy to local deploy folder"""
        print("\n📂 Deploying locally...")
        
        deploy_path = Path.home() / "Desktop" / "WebAnalytics_Deploy"
        deploy_path.mkdir(exist_ok=True)
        
        import shutil
        exe_path = self.dist_folder / "WebAnalytics.exe"
        if exe_path.exists():
            shutil.copy(exe_path, deploy_path)
            print(f"✅ Deployed to: {deploy_path}")
            
            # Create README
            readme = deploy_path / "README.txt"
            readme.write_text("""
Web Analytics Dashboard v1.0
============================

HOW TO USE:
1. Double click WebAnalytics.exe
2. Enter URL and click "Analyze & Save"
3. View data in "Raw Data" tab
4. View charts in "Analytics" tab

TROUBLESHOOTING:
- If crash: Check logs/ folder
- If button not working: Restart app
- Database issues: Delete data/analytics.db

Support: github.com/yourrepo
            """)
            print("📄 README created")
            return True
        else:
            print("❌ EXE not found. Build first.")
            return False
    
    def auto_fix_common_issues(self):
        """Tự động fix các vấn đề phổ biến trước deploy"""
        print("\n🔧 Auto-fixing common issues...")
        
        # Fix 1: Create required folders
        for folder in ['data', 'logs', 'assets']:
            path = self.project_root / folder
            path.mkdir(exist_ok=True)
            print(f"  ✅ Folder: {folder}")
        
        # Fix 2: Check main.py has AA_ShareOpenGLContexts
        main_py = self.project_root / "main.py"
        # Đọc file với UTF-8 để tránh UnicodeDecodeError trên Windows
        content = main_py.read_text(encoding="utf-8", errors="ignore")
        if 'AA_ShareOpenGLContexts' not in content:
            print("  ⚠️ Adding QWebEngine fix to main.py")
            fixed = content.replace(
                'from gui.main_window',
                'from PyQt6.QtCore import Qt\nQApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)\n\nfrom gui.main_window'
            )
            # Ghi lại với UTF-8
            main_py.write_text(fixed, encoding="utf-8")
            print("  ✅ QWebEngine fix added")

        return True
    
    def full_deploy(self):
        """Full deployment pipeline"""
        print("=" * 60)
        print("🚀 AUTO-DEPLOY PIPELINE STARTING...")
        print("=" * 60)
        
        steps = [
            ("Auto-fix", self.auto_fix_common_issues),
            ("Dependencies", self.check_dependencies),
            ("Tests", self.run_tests),
            ("Build", self.build_exe),
            ("Deploy", self.deploy_local),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{'='*60}")
            print(f"STEP: {step_name}")
            print("="*60)
            
            if not step_func():
                print(f"\n❌ Pipeline failed at: {step_name}")
                return False
        
        print("\n" + "="*60)
        print("✅ DEPLOYMENT SUCCESSFUL!")
        print("="*60)
        print(f"📦 App ready at: {Path.home() / 'Desktop' / 'WebAnalytics_Deploy'}")
        return True

if __name__ == "__main__":
    deployer = AutoDeployer()
    deployer.full_deploy()
