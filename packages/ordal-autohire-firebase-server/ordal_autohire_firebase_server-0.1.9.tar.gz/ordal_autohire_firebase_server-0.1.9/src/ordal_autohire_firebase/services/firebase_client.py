import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import logging

logger = logging.getLogger(__name__)
_db = None

def get_db():
    global _db
    if _db is None:
        try:
            load_dotenv()
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            
            if not cred_path:
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set")
            
            if not os.path.exists(cred_path):
                raise FileNotFoundError(f"Credentials file not found at: {cred_path}")
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    return _db