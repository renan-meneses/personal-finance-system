from pymongo import MongoClient
from django.conf import settings


def get_mongo_client() -> MongoClient:
    return MongoClient(settings.MONGO_URI)


def get_mongo_db():
    client = get_mongo_client()
    return client[settings.MONGO_DB_NAME]


def ping_mongo() -> bool:
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return True
    except Exception:
        return False
