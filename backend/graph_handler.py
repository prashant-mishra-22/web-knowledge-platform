# backend/graph_handler.py
from pymongo import MongoClient
import os
from datetime import datetime

class MongoDBGraphHandler:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.get_database()
        
        self.entities = self.db["entities"]
        self.relationships = self.db["relationships"]
        self.domain_graphs = self.db["domain_graphs"]
    
    def add_entity(self, entity_data):
        entity_data["created_at"] = datetime.utcnow()
        entity_data["updated_at"] = datetime.utcnow()
        self.entities.update_one(
            {"name": entity_data["name"], "type": entity_data["type"]},
            {"$set": entity_data, "$inc": {"evidence_count": 1}},
            upsert=True
        )
        return entity_data["name"]
    
    def get_stats(self):
        return {
            "entities": self.entities.count_documents({}),
            "relationships": self.relationships.count_documents({}),
            "domain_graphs": self.domain_graphs.count_documents({})
        }