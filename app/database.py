import os
import json
import uuid
import datetime

# Database Mode indicator
DB_MODE = "local" # Default to local
db_client = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Try to initialize Firebase
    cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db_client = firestore.client()
        DB_MODE = "firebase"
        print("[DATABASE] Successfully connected to Firebase Firestore.")
    else:
        print(f"[DATABASE] Firebase credentials key '{cred_path}' not found. Falling back to Local JSON mode.")
except Exception as e:
    print(f"[DATABASE] Firebase initialization failed: {e}. Falling back to Local JSON mode.")

LOCAL_DB_FILE = os.environ.get("LOCAL_DB_PATH", "local_db.json")

# Ensure local JSON database has a default template and mock products
def _init_local_db():
    if not os.path.exists(LOCAL_DB_FILE):
        default_data = {
            "users": {},
            "products": {
                "prod_1": {
                    "id": "prod_1",
                    "name": "Fresh Organic Tomatoes",
                    "category": "Vegetables",
                    "price": 120.0,
                    "unit": "per kg",
                    "description": "Lush red tomatoes harvested directly from local farms. Rich in flavor and perfect for stews or salads.",
                    "image_url": "/static/images/tomatoes.jpg",
                    "in_stock": True,
                    "created_at": datetime.datetime.now().isoformat()
                },
                "prod_2": {
                    "id": "prod_2",
                    "name": "Sweet Red Apples",
                    "category": "Fruits",
                    "price": 250.0,
                    "unit": "per kg",
                    "description": "Crisp, sweet, and juicy red apples. Perfect for a healthy snack or making delicious pies.",
                    "image_url": "/static/images/apples.jpg",
                    "in_stock": True,
                    "created_at": datetime.datetime.now().isoformat()
                },
                "prod_3": {
                    "id": "prod_3",
                    "name": "Fresh Green Lemons",
                    "category": "Fruits",
                    "price": 80.0,
                    "unit": "per kg",
                    "description": "Zesty and juicy lemons, great for dressings, beverages, and adding a fresh citrus touch to meals.",
                    "image_url": "/static/images/Lemons.jpg",
                    "in_stock": True,
                    "created_at": datetime.datetime.now().isoformat()
                },
                "prod_4": {
                    "id": "prod_4",
                    "name": "Irish Potatoes",
                    "category": "Grains",
                    "price": 95.0,
                    "unit": "per kg",
                    "description": "Premium quality Irish potatoes, ideal for roasting, baking, boiling, or making fresh potato chips.",
                    "image_url": "/static/images/potatoes.jpg",
                    "in_stock": True,
                    "created_at": datetime.datetime.now().isoformat()
                },
                "prod_5": {
                    "id": "prod_5",
                    "name": "Fresh Collard Greens (Sukuma Wiki)",
                    "category": "Vegetables",
                    "price": 50.0,
                    "unit": "per bunch",
                    "description": "Fresh, locally-grown collard greens (Sukuma Wiki), hand-picked daily. High in nutrients and extremely delicious.",
                    "image_url": "/static/images/kale.jpg",
                    "in_stock": True,
                    "created_at": datetime.datetime.now().isoformat()
                }
            },
            "orders": {}
        }
        with open(LOCAL_DB_FILE, 'w') as f:
            json.dump(default_data, f, indent=4)

if DB_MODE == "local":
    _init_local_db()


def _read_local_db():
    try:
        with open(LOCAL_DB_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[DATABASE ERROR] Could not read local DB: {e}")
        return {"users": {}, "products": {}, "orders": {}}

def _write_local_db(data):
    try:
        with open(LOCAL_DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)
            return True
    except Exception as e:
        print(f"[DATABASE ERROR] Could not write to local DB: {e}")
        return False

# Database API Operations

def get_document(collection, doc_id):
    """Retrieves a single document from a collection by ID."""
    if DB_MODE == "firebase":
        doc = db_client.collection(collection).document(str(doc_id)).get()
        return doc.to_dict() if doc.exists else None
    else:
        db_data = _read_local_db()
        return db_data.get(collection, {}).get(str(doc_id), None)

def get_documents(collection):
    """Retrieves all documents in a collection."""
    if DB_MODE == "firebase":
        docs = db_client.collection(collection).stream()
        return [doc.to_dict() for doc in docs]
    else:
        db_data = _read_local_db()
        return list(db_data.get(collection, {}).values())

def add_document(collection, data, doc_id=None):
    """Adds a document to a collection. Generates an ID if not specified."""
    if not doc_id:
        doc_id = str(uuid.uuid4())
    
    # Standardize data ID field
    data['id'] = doc_id
    if 'created_at' not in data:
        data['created_at'] = datetime.datetime.now().isoformat()

    if DB_MODE == "firebase":
        db_client.collection(collection).document(str(doc_id)).set(data)
        return doc_id
    else:
        db_data = _read_local_db()
        if collection not in db_data:
            db_data[collection] = {}
        db_data[collection][str(doc_id)] = data
        _write_local_db(db_data)
        return doc_id

def update_document(collection, doc_id, data):
    """Updates specific fields of an existing document."""
    if DB_MODE == "firebase":
        db_client.collection(collection).document(str(doc_id)).update(data)
        return True
    else:
        db_data = _read_local_db()
        col = db_data.get(collection, {})
        if str(doc_id) in col:
            col[str(doc_id)].update(data)
            _write_local_db(db_data)
            return True
        return False

def delete_document(collection, doc_id):
    """Removes a document from a collection."""
    if DB_MODE == "firebase":
        db_client.collection(collection).document(str(doc_id)).delete()
        return True
    else:
        db_data = _read_local_db()
        col = db_data.get(collection, {})
        if str(doc_id) in col:
            del col[str(doc_id)]
            _write_local_db(db_data)
            return True
        return False

def query_documents(collection, field, operator, value):
    """Performs a query filtering documents by field value."""
    if DB_MODE == "firebase":
        # Convert standard operators to Firestore where operators
        # Firestore uses: '==', '<', '<=', '>', '>=', 'in', 'array-contains', etc.
        docs = db_client.collection(collection).where(field, operator, value).stream()
        return [doc.to_dict() for doc in docs]
    else:
        db_data = _read_local_db()
        col = db_data.get(collection, {})
        results = []
        for doc in col.values():
            doc_val = doc.get(field, None)
            match = False
            if operator == "==":
                match = (doc_val == value)
            elif operator == "!=":
                match = (doc_val != value)
            elif operator == ">":
                match = (doc_val is not None and doc_val > value)
            elif operator == "<":
                match = (doc_val is not None and doc_val < value)
            elif operator == ">=":
                match = (doc_val is not None and doc_val >= value)
            elif operator == "<=":
                match = (doc_val is not None and doc_val <= value)
            elif operator == "in":
                match = (doc_val in value)
            
            if match:
                results.append(doc)
        return results
