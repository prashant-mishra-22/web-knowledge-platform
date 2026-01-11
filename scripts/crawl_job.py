# scripts/crawl_job.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from crawlers.scraper import SimpleCrawler
from crawlers.extractor import SimpleExtractor
from backend.models import SessionLocal, RawCrawl, URLFrame, DomainFrame
from backend.graph_handler import MongoDBGraphHandler
from datetime import datetime

def run_crawl_job():
    print("🚀 Starting production crawl job...")
    
    crawler = SimpleCrawler()
    extractor = SimpleExtractor()
    graph_handler = MongoDBGraphHandler()
    
    # Sample Indian websites to crawl
    websites = [
        "https://www.tatasteel.com",
        "https://www.jsw.in",
        "https://www.mahindra.com",
        "https://www.infosys.com",
        "https://www.tcs.com",
        "https://www.wipro.com",
        "https://www.hcltech.com",
        "https://www.ril.com",
        "https://www.adani.com",
        "https://www.britannia.co.in"
    ]
    
    urls_crawled = 0
    
    for website in websites:
        print(f"Crawling: {website}")
        
        # Fetch the website
        data = crawler.fetch_url(website)
        if not data:
            continue
        
        db = SessionLocal()
        try:
            # Save raw data
            raw = RawCrawl(
                url=data['url'],
                domain=data['domain'],
                raw_html=data['content'],
                headers=data['headers'],
                status_code=data['status_code'],
                content_hash=data['content_hash']
            )
            db.add(raw)
            db.commit()
            
            # Extract knowledge
            extracted = extractor.extract_from_html(data['content'])
            
            # Save URL frame
            frame = URLFrame(
                url=data['url'],
                domain=data['domain'],
                metadata=extracted['metadata'],
                entities=extracted['entities'],
                contacts=extracted['contacts'],
                confidence_score=0.8
            )
            db.add(frame)
            db.commit()
            
            # Update domain frame
            domain_frame = db.query(DomainFrame).filter(DomainFrame.domain == data['domain']).first()
            if domain_frame:
                domain_frame.url_count += 1
                domain_frame.last_crawled = datetime.utcnow()
                # Update contacts
                current_contacts = domain_frame.aggregated_contacts or {'emails': [], 'phones': []}
                current_contacts['emails'].extend(extracted['contacts']['emails'])
                current_contacts['phones'].extend(extracted['contacts']['phones'])
                # Remove duplicates
                current_contacts['emails'] = list(set(current_contacts['emails']))[:10]
                current_contacts['phones'] = list(set(current_contacts['phones']))[:10]
                domain_frame.aggregated_contacts = current_contacts
            else:
                domain_frame = DomainFrame(
                    domain=data['domain'],
                    aggregated_contacts=extracted['contacts'],
                    url_count=1,
                    last_crawled=datetime.utcnow(),
                    confidence_score=0.8
                )
                db.add(domain_frame)
            
            db.commit()
            
            # Add to knowledge graph
            for entity in extracted['entities'][:5]:
                graph_handler.add_entity({
                    "name": entity['text'],
                    "type": entity['label'],
                    "source_url": data['url']
                })
            
            urls_crawled += 1
            print(f"✅ Crawled: {data['url']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.rollback()
        finally:
            db.close()
    
    print(f"🎉 Crawl job completed! Crawled {urls_crawled} websites.")

if __name__ == "__main__":
    run_crawl_job()