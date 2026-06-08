from datetime import datetime
from mongodb_utils.client import get_mongo_db
from bson.objectid import ObjectId

COLLECTION_NAME = "transactions"


def serialize_transaction(t):
    t["_id"] = str(t["_id"])
    return t


def list_transactions(user_id, filters=None, page=1, page_size=50):
    db = get_mongo_db()
    query = {"user_id": user_id}
    if filters:
        query.update(filters)
    skip = (page - 1) * page_size
    cursor = (
        db[COLLECTION_NAME]
        .find(query)
        .sort("date", -1)
        .skip(skip)
        .limit(page_size)
    )
    total = db[COLLECTION_NAME].count_documents(query)
    items = [serialize_transaction(t) for t in cursor]
    return items, total


def create_transaction(data):
    db = get_mongo_db()
    data["created_at"] = datetime.utcnow().isoformat()
    data["updated_at"] = datetime.utcnow().isoformat()
    result = db[COLLECTION_NAME].insert_one(data)
    return serialize_transaction(db[COLLECTION_NAME].find_one({"_id": result.inserted_id}))


def get_transaction(transaction_id):
    db = get_mongo_db()
    t = db[COLLECTION_NAME].find_one({"_id": ObjectId(transaction_id)})
    if t:
        return serialize_transaction(t)
    return None


def update_transaction(transaction_id, data):
    db = get_mongo_db()
    data["updated_at"] = datetime.utcnow().isoformat()
    db[COLLECTION_NAME].update_one(
        {"_id": ObjectId(transaction_id)}, {"$set": data}
    )
    return get_transaction(transaction_id)


def delete_transaction(transaction_id):
    db = get_mongo_db()
    result = db[COLLECTION_NAME].delete_one({"_id": ObjectId(transaction_id)})
    return result.deleted_count > 0


def bulk_insert(transactions_list):
    db = get_mongo_db()
    now = datetime.utcnow().isoformat()
    for t in transactions_list:
        t["created_at"] = now
        t["updated_at"] = now
    result = db[COLLECTION_NAME].insert_many(transactions_list)
    return len(result.inserted_ids)


def get_audit_collection():
    db = get_mongo_db()
    return db["audit_trails"]
