# backend/models.py - UPDATED FOR RAILWAY MONGODB
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import os
from datetime import datetime
import urllib.parse

# PostgreSQL for Railway
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL or "postgresql://temp:temp@localhost/temp")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB for Railway - FIXED
MONGODB_URI = os.getenv("MONGODB_URI")

if MONGODB_URI:
    # Parse the URI to get database name
    try:
        parsed_uri = urllib.parse.urlparse(MONGODB_URI)
        database_name = parsed_uri.path.strip('/') or 'knowledge_graph'
        
        # Connect to MongoDB
        mongo_client = MongoClient(MONGODB_URI)
        mongo_db = mongo_client[database_name]
        
        print(f"✅ Connected to MongoDB database: {database_name}")
    except Exception as e:
        print(f"⚠️ MongoDB connection error: {e}")
        # Fallback to in-memory for now
        mongo_client = None
        mongo_db = None
else:
    print("⚠️ MONGODB_URI not set, using fallback")
    mongo_client = None
    mongo_db = None

# Collections - with fallback
if mongo_db:
    entities_col = mongo_db["entities"]
    relationships_col = mongo_db["relationships"]
    domain_graphs_col = mongo_db["domain_graphs"]
else:
    # Create dummy collections for now
    entities_col = None
    relationships_col = None
    domain_graphs_col = None

# PostgreSQL Models
class RawCrawl(Base):
    __tablename__ = "raw_crawls"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    domain = Column(String, index=True)
    raw_html = Column(Text)
    headers = Column(JSON)
    status_code = Column(Integer)
    content_hash = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class URLFrame(Base):
    __tablename__ = "url_frames"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    domain = Column(String, index=True)
    metadata = Column(JSON)
    entities = Column(JSON)
    relations = Column(JSON)
    contacts = Column(JSON)
    topics = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

class DomainFrame(Base):
    __tablename__ = "domain_frames"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True)
    company_name = Column(String, nullable=True)
    industry = Column(JSON, default=list)
    aggregated_contacts = Column(JSON)
    dominant_topics = Column(JSON)
    confidence_score = Column(Float, default=0.0)
    url_count = Column(Integer, default=0)
    last_crawled = Column(DateTime, nullable=True)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
except Exception as e:

    print(f"⚠️ Could not create tables: {e}")
