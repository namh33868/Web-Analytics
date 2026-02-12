# 🌐 Web Analytics Dashboard

Professional desktop application for analyzing website metrics with beautiful data visualization.

![App Screenshot](assets/screenshot.png)

## ✨ Features

- 🚀 **Fast Web Scraping** - Analyze any website in seconds
- 📊 **Beautiful Dashboard** - Interactive charts and metrics
- 💾 **Local Database** - SQLite storage for privacy
- 🔄 **Auto-Update** - One-click updates from GitHub
- 🎨 **Dark Theme** - Modern scientific UI
- 📈 **Analytics**:
  - Word count analysis
  - Internal/external link tracking
  - Image statistics
  - Top content pages

## 🖥️ Screenshots

| Dashboard | Analytics |
|-----------|-----------|
| <img width="1396" height="867" alt="image" src="https://github.com/user-attachments/assets/ac4182c6-d288-4a6c-b972-19e52f9b8bd8" /> | <img width="1917" height="1022" alt="image" src="https://github.com/user-attachments/assets/4f9605a0-6701-4943-8b47-950b08217f81" />
 |

## 📦 Installation

### Option 1: Download EXE (Windows)
1. Go to [Releases](https://github.com/yourusername/web-analytics/releases)
2. Download `WebAnalytics.exe`
3. Run it! No installation needed.

### Option 2: Run from Source

**Requirements:**
- Python 3.10+
- Windows 10/11 (or Linux/Mac with PyQt6 support)

**Steps:**
```bash
# 1. Clone repository
git clone https://github.com/yourusername/web-analytics.git
cd web-analytics

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python main.py
```
## 🚀 Usage

Enter URL in the input field (e.g., https://example.com)

Click "Analyze & Save" to start scraping

View Results:

Raw Data tab: Table with all metrics

Analytics tab: Charts and visualizations

Auto-Update: Click "Check Updates" to get latest version

## 🛠️ Build from Source
``` bash
# Build standalone EXE
python deploy/auto_deploy.py

# Output: dist/WebAnalytics.exe
```
## 🔧 Configuration
``` bash
Edit utils/config.py:

python
SCRAPE_TIMEOUT = 10        # Request timeout (seconds)
MAX_CRAWL_DEPTH = 2        # Recursive crawl depth
USER_AGENT = "YourBot/1.0" # Custom user agent
```
## 📁 Project Structure
text
web-analytics/
├── main.py              # Entry point
├── gui/                 # UI components
├── core/                # Business logic
├── utils/               # Utilities
├── deploy/              # Build scripts
└── data/                # Local database (not in repo)
## 🤝 Contributing
1. Fork the repository

2. Create feature branch (git checkout -b feature/amazing)

3. Commit changes (git commit -m 'Add feature')

4. Push to branch (git push origin feature/amazing)

5. Open Pull Request

## 🐛 Known Issues
QWebEngineView error: Fixed automatically by main.py

Unicode errors: Use UTF-8 encoding for all files

Slow scraping: Increase SCRAPE_TIMEOUT in config

## 📝 Changelog
v1.0.0 (2026-02-12)
# ✨ Initial release

# 🎨 Dark theme UI

# 📊 Basic analytics features

# 🔄 Auto-update system

## 📄 License
MIT License - see LICENSE file

## 💬 Support
Issues: GitHub Issues

Discussions: GitHub Discussions

Email: your.email@example.com

## 🙏 Acknowledgments
PyQt6 - GUI framework

BeautifulSoup4 - Web scraping

Plotly - Data visualization

## ⭐ Star this repo if you find it helpful!
