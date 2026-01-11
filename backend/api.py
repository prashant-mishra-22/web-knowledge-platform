# backend/api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
from .models import SessionLocal, URLFrame, DomainFrame
from .graph_handler import MongoDBGraphHandler

app = FastAPI(title="Web Knowledge Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

graph_handler = MongoDBGraphHandler()

class QueryRequest(BaseModel):
    query: str
    max_results: int = 10

@app.get("/")
async def root():
    return {"message": "Web Knowledge Platform API", "status": "active"}

@app.get("/stats")
async def get_stats():
    db = SessionLocal()
    try:
        url_count = db.query(URLFrame).count()
        domain_count = db.query(DomainFrame).count()
        graph_stats = graph_handler.get_stats()
        
        return {
            "urls_crawled": url_count,
            "domains_processed": domain_count,
            "entities_in_graph": graph_stats["entities"],
            "relationships_in_graph": graph_stats["relationships"],
            "status": "active",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e), "urls_crawled": 0, "domains_processed": 0}
    finally:
        db.close()

@app.post("/query")
async def query_knowledge(request: QueryRequest):
    try:
        db = SessionLocal()
        domains = db.query(DomainFrame).filter(
            DomainFrame.aggregated_contacts != None
        ).limit(request.max_results).all()
        
        results = []
        for domain in domains:
            contacts = domain.aggregated_contacts or {}
            if isinstance(contacts, dict):
                emails = contacts.get('emails', [])[:3]
                phones = contacts.get('phones', [])[:3]
                
                if emails or phones:
                    results.append({
                        'domain': domain.domain,
                        'company_name': domain.company_name or domain.domain,
                        'contacts': {'emails': emails, 'phones': phones},
                        'confidence': domain.confidence_score,
                        'url_count': domain.url_count
                    })
        
        return {"results": results, "total": len(results)}
    except Exception as e:
        return {"error": str(e), "results": [], "total": 0}