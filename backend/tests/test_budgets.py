from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.finance.models import CategoryBudget, Notification


class BudgetAlertTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="budgetuser", password="testpass123"
        )
        self.client.login(username="budgetuser", password="testpass123")

    def _create_budget(self, category="food", limit=1000, current=0):
        return CategoryBudget.objects.create(
            user=self.user,
            category=category,
            limit_amount=limit,
            current_spend=current,
            month=12,
            year=2024,
        )

    def test_budget_80_percent_alert(self):
        budget = self._create_budget(current=800)
        self.assertTrue(budget.needs_alert_80)
        self.assertFalse(budget.needs_alert_100)

    def test_budget_100_percent_alert(self):
        budget = self._create_budget(current=1000)
        self.assertTrue(budget.needs_alert_80)
        self.assertTrue(budget.needs_alert_100)
        self.assertEqual(budget.spend_percentage, 100.0)

    def test_budget_below_threshold(self):
        budget = self._create_budget(current=500)
        self.assertFalse(budget.needs_alert_80)
        self.assertFalse(budget.needs_alert_100)

    def test_budget_zero_limit_does_not_crash(self):
        budget = CategoryBudget.objects.create(
            user=self.user,
            category="transport",
            limit_amount=0,
            current_spend=0,
            month=12,
            year=2024,
        )
        self.assertEqual(budget.spend_percentage, 0.0)

    def test_create_budget_via_api(self):
        payload = {
            "category": "food",
            "limit_amount": "2000.00",
            "current_spend": "0.00",
            "month": 1,
            "year": 2025,
        }
        response = self.client.post("/api/budgets/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["category"], "food")
        self.assertEqual(float(data["limit_amount"]), 2000.00)

    def test_list_budgets(self):
        self._create_budget(category="food")
        self._create_budget(category="transport", limit=500)
        response = self.client.get("/api/budgets/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_budget_percentage_view(self):
        budget = self._create_budget(current=300)
        response = self.client.get(f"/api/budgets/{budget.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("spend_percentage", response.json())
        self.assertEqual(response.json()["spend_percentage"], 30.0)
