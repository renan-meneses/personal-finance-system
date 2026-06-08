from celery import shared_task
from mongodb_utils.client import get_mongo_db
from apps.transactions.management.commands.categorize_transactions import CATEGORY_RULES
import re


@shared_task
def auto_categorize(user_id: int | None = None):
    db = get_mongo_db()
    collection = db["transactions"]
    query = {"category": {"$in": ["other", "", None]}}
    if user_id:
        query["user_id"] = user_id

    uncategorized = collection.find(query)
    updated = 0
    for tx in uncategorized:
        desc = tx.get("description", "")
        for pattern, category in CATEGORY_RULES:
            if re.search(pattern, desc):
                collection.update_one(
                    {"_id": tx["_id"]},
                    {"$set": {"category": category}},
                )
                updated += 1
                break

    return f"Categorized {updated} transactions"
