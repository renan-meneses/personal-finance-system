import json
from decimal import Decimal
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.finance.models import CategoryBudget
from mongodb_utils.client import get_mongo_db


@override_settings(MONGO_URI="mongodb://localhost:27017", MONGO_DB_NAME="test_finance")
class TransactionAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client.login(username="testuser", password="testpass123")

        # Clean test MongoDB collection
        db = get_mongo_db()
        db["transactions"].delete_many({})

    def tearDown(self):
        db = get_mongo_db()
        db["transactions"].delete_many({})

    def test_create_transaction(self):
        payload = {
            "date": "2024-12-01",
            "description": "Uber ride",
            "amount": 25.50,
            "type": "expense",
            "category": "transport",
        }
        response = self.client.post(
            "/api/transactions/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["description"], "Uber ride")
        self.assertEqual(float(data["amount"]), 25.50)
        self.assertEqual(data["category"], "transport")

    def test_list_transactions_empty(self):
        response = self.client.get("/api/transactions/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 0)

    def test_create_income_transaction(self):
        payload = {
            "date": "2024-12-01",
            "description": "Salary deposit",
            "amount": 5000.00,
            "type": "income",
            "category": "salary",
        }
        response = self.client.post(
            "/api/transactions/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["type"], "income")

    def test_create_recurring_transaction(self):
        payload = {
            "date": "2024-12-01",
            "description": "Netflix subscription",
            "amount": 19.90,
            "type": "expense",
            "category": "entertainment",
            "is_recurring": True,
            "next_execution_date": "2025-01-01",
        }
        response = self.client.post(
            "/api/transactions/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["is_recurring"])

    def test_unauthenticated_request_fails(self):
        self.client.logout()
        payload = {"date": "2024-12-01", "description": "Test", "amount": 10, "type": "expense"}
        response = self.client.post(
            "/api/transactions/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_health_check(self):
        response = self.client.get("/api/health/")
        self.assertIn(response.status_code, (200, 503))
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("databases", data)
