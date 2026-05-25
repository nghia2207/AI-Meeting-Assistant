"""
Database Configuration - Kết nối MongoDB Atlas
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

_client = None
_db = None

# In-memory storage for testing (when MongoDB is not available)
_in_memory_store = {
    'meetings': []
}

def get_database():
    """Kết nối MongoDB và trả về database instance"""
    global _client, _db

    if _db is not None:
        return _db

    mongo_uri = os.getenv('MONGODB_URI')

    if not mongo_uri:
        print('[WARNING] MongoDB not configured, using in-memory storage')
        return None

    try:
        _client = MongoClient(
            mongo_uri,
            maxPoolSize=10,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=45000
        )

        # Test connection
        _client.admin.command('ping')

        # Extract database name from URI
        db_name = 'meeting-assistant'
        if '/ ' in mongo_uri:
            db_name = mongo_uri.split('/')[-1].split('?')[0]

        _db = _client[db_name]
        print('[OK] MongoDB connection established')
        return _db

    except Exception as e:
        print(f'MongoDB connection failed: {e}')
        print('[WARNING] Using in-memory storage instead')
        return None

def get_meetings_collection():
    """Lấy meetings collection (hoặc in-memory store)"""
    db = get_database()
    if db is None:
        return None
    return db['meetings']

def is_using_memory():
    """Kiểm tra có đang dùng in-memory storage không"""
    return get_database() is None