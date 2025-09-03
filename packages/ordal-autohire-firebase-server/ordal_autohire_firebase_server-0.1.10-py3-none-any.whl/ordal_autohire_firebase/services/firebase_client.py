import os, json
import firebase_admin
from firebase_admin import credentials, firestore

_db = None

def _make_cred():
    js = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if js and js.strip().lower() != "none":
        return credentials.Certificate(json.loads(js))
    if path and path.strip().lower() != "none":
        return credentials.Certificate(path)
    return credentials.ApplicationDefault()

def get_db():
    global _db
    if _db is not None:
        return _db
    if not firebase_admin._apps:
        cred = _make_cred()
        firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db
