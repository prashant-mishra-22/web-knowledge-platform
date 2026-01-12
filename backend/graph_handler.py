# backend/graph_handler.py - UPDATED
from pymongo import MongoClient
import os
from datetime import datetime
import urllib.parse

class MongoDBGraphHandler:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI")
        if not self.mongo_uri:
            print("⚠️ MONGODB_URI not set")
            self.client = None
            self.db = None
            return
        
        try:
            # Parse database name from URI
            parsed_uri = urllib.parse.urlparse(self.mongo_uri)
            database_name = parsed_uri.path.strip('/') or 'knowledge_graph'
            
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[database_name]
            
            self.entities = self.db["entities"]
            self.relationships = self.db["relationships"]
            self.domain_graphs = self.db["domain_graphs"]
            
            print(f"✅ Graph handler connected to MongoDB: {database_name}")
        except Exception as e:
            print(f"❌ Graph handler error: {e}")
            self.client = None
            self.db = None
    
    def add_entity(self, entity_data):
        if not self.db:
            return entity_data.get("name", "unknown")
        
        entity_data["created_at"] = datetime.utcnow()
        entity_data["updated_at"] = datetime.utcnow()
        
        try:
            self.entities.update_one(
                {"name": entity_data["name"], "type": entity_data["type"]},
                {"$set": entity_data, "$inc": {"evidence_count": 1}},
                upsert=True
            )
            return entity_data["name"]
        except Exception as e:
            print(f"Error adding entity: {e}")
            return entity_data.get("name", "unknown")
    
    def get_stats(self):
        if not self.db:
            return {"entities": 0, "relationships": 0, "domain_graphs": 0}
        
        try:
            return {
                "entities": self.entities.count_documents({}),
                "relationships": self.relationships.count_documents({}),
                "domain_graphs": self.domain_graphs.count_documents({})
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"entities": 0, "relationships": 0, "domain_graphs": 0}
