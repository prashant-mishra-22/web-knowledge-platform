# crawlers/scraper.py
import requests
import hashlib
from datetime import datetime
import time

class SimpleCrawler:
    def fetch_url(self, url):
        try:
            headers = {
                'User-Agent': 'KnowledgeBot/1.0'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            content_hash = hashlib.sha256(response.text.encode()).hexdigest()
            
            return {
                'url': url,
                'domain': url.split('/')[2],
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'content_hash': content_hash,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None