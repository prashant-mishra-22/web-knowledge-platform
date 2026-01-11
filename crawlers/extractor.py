# crawlers/extractor.py
import re
from bs4 import BeautifulSoup

class SimpleExtractor:
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'\b(?:\+?91[\s-]?)?[6789]\d{9}\b'
    
    def extract_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove scripts
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        
        # Extract metadata
        metadata = {
            'title': soup.title.string if soup.title else '',
            'description': ''
        }
        
        # Extract contacts
        emails = re.findall(self.email_pattern, text)
        phones = re.findall(self.phone_pattern, text)
        
        # Simple entity extraction (just find company-like words)
        entities = []
        words = text.split()
        for word in words:
            if word.istitle() and len(word) > 2 and word.lower() not in ['the', 'and', 'for']:
                entities.append({'text': word, 'label': 'ORG'})
        
        return {
            'metadata': metadata,
            'entities': entities[:10],  # Limit to 10
            'contacts': {
                'emails': list(set(emails[:5])),
                'phones': list(set(phones[:5]))
            }
        }