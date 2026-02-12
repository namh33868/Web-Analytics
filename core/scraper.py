# core/scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from utils.config import SCRAPE_TIMEOUT, USER_AGENT

class WebScraper:
    @staticmethod
    def analyze_single_page(url: str) -> dict:
        """
        Thu thập dữ liệu từ 1 URL duy nhất
        Returns: dict chứa các metrics
        """
        headers = {'User-Agent': USER_AGENT}
        try:
            response = requests.get(url, headers=headers, timeout=SCRAPE_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Trích xuất dữ liệu chính
            title = soup.title.string.strip() if soup.title else "No title"
            
            # Đếm từ (text từ p, h1-h6, li)
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            full_text = ' '.join([el.get_text() for el in text_elements])
            word_count = len(full_text.split())
            
            # Đếm ảnh và link
            img_count = len(soup.find_all('img'))
            
            # Phân loại internal/external links
            domain = urlparse(url).netloc
            internal, external = 0, 0
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/'):  # Relative URL
                    internal += 1
                elif urlparse(href).netloc == domain:
                    internal += 1
                else:
                    external += 1
            
            return {
                'url': url,
                'title': title,
                'word_count': word_count,
                'img_count': img_count,
                'internal_links': internal,
                'external_links': external
            }
            
        except Exception as e:
            return {'url': url, 'error': str(e), 'word_count': 0, 'img_count': 0, 
                   'internal_links': 0, 'external_links': 0}
