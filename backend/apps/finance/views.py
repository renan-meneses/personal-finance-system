from decimal import Decimal
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from apps.users.models import UserProfile
from apps.finance.models import (
    CategoryBudget, CreditCard, CreditCardStatement,
    FinancialGoal, InvestmentPortfolio, Notification,
)
from apps.finance.serializers import (
    CategoryBudgetSerializer, CreditCardSerializer,
    CreditCardStatementSerializer, FinancialGoalSerializer,
    InvestmentPortfolioSerializer, NotificationSerializer,
)
from apps.transactions.models import Transaction
from mongodb_utils.client import get_mongo_db


class CategoryBudgetViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryBudgetSerializer

    def get_queryset(self):
        return CategoryBudget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreditCardViewSet(viewsets.ModelViewSet):
    serializer_class = CreditCardSerializer

    def get_queryset(self):
        return CreditCard.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreditCardStatementViewSet(viewsets.ModelViewSet):
    serializer_class = CreditCardStatementSerializer

    def get_queryset(self):
        return CreditCardStatement.objects.filter(
            credit_card__user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save()


class FinancialGoalViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialGoalSerializer

    def get_queryset(self):
        return FinancialGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InvestmentPortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentPortfolioSerializer

    def get_queryset(self):
        return InvestmentPortfolio.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "ok"})


@api_view(["GET"])
def cash_flow_projection(request):
    days = request.query_params.get("days", 30)
    try:
        days = int(days)
    except ValueError:
        days = 30

    profile = UserProfile.objects.get(user=request.user)
    monthly_income = float(profile.monthly_income)
    current_balance = float(
        request.query_params.get("current_balance", 0)
    )

    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=days)

    db = get_mongo_db()
    transactions_collection = db["transactions"]

    # Predicted income for the period
    income_per_month = monthly_income
    months_in_period = max(1, days / 30.0)
    predicted_income = income_per_month * months_in_period

    # Scheduled expenses from recurring transactions
    recurring = list(
        transactions_collection.find(
            {
                "user_id": request.user.id,
                "is_recurring": True,
                "next_execution_date": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat(),
                },
            }
        )
    )
    scheduled_expenses = sum(
        float(t.get("amount", 0)) for t in recurring if t.get("type") == "expense"
    )

    # Cash flow projection for each day
    projections = []
    running_balance = current_balance
    for day_offset in range(days):
        current_day = start_date + timedelta(days=day_offset)
        day_income = 0.0
        day_expense = 0.0

        if current_day.day == 1:
            day_income = income_per_month

        for t in recurring:
            exec_date_str = t.get("next_execution_date")
            if exec_date_str:
                try:
                    exec_date = date.fromisoformat(exec_date_str)
                except (ValueError, TypeError):
                    continue
                if exec_date == current_day:
                    amt = float(t.get("amount", 0))
                    if t.get("type") == "income":
                        day_income += amt
                    else:
                        day_expense += amt

        running_balance += day_income - day_expense
        projections.append(
            {
                "date": current_day.isoformat(),
                "balance": round(running_balance, 2),
                "income": round(day_income, 2),
                "expense": round(day_expense, 2),
            }
        )

    return Response(
        {
            "days": days,
            "current_balance": round(current_balance, 2),
            "predicted_income": round(predicted_income, 2),
            "scheduled_expenses": round(scheduled_expenses, 2),
            "projected_balance": round(running_balance, 2),
            "daily_projections": projections,
        }
    )


@api_view(["GET"])
def dashboard_summary(request):
    user = request.user
    db = get_mongo_db()
    transactions_collection = db["transactions"]

    # Aggregate total expenses and income
    pipeline_expense = [
        {"$match": {"user_id": user.id, "type": "expense"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]
    pipeline_income = [
        {"$match": {"user_id": user.id, "type": "income"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
    ]
    expense_result = list(transactions_collection.aggregate(pipeline_expense))
    income_result = list(transactions_collection.aggregate(pipeline_income))

    total_expenses = float(expense_result[0]["total"]) if expense_result else 0.0
    total_income = float(income_result[0]["total"]) if income_result else 0.0

    # Expenses by category
    category_pipeline = [
        {"$match": {"user_id": user.id, "type": "expense"}},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
        {"$sort": {"total": -1}},
    ]
    category_expenses = {
        c["_id"] or "other": float(c["total"])
        for c in transactions_collection.aggregate(category_pipeline)
    }

    # Goals
    goals = FinancialGoal.objects.filter(user=user)
    goals_data = FinancialGoalSerializer(goals, many=True).data

    # Investments summary
    investments = InvestmentPortfolio.objects.filter(user=user)
    total_invested = sum(i.total_invested for i in investments)
    total_current = sum(i.current_value for i in investments)

    # Upcoming recurring
    today = timezone.now().date().isoformat()
    recurring = list(
        transactions_collection.find(
            {
                "user_id": user.id,
                "is_recurring": True,
                "next_execution_date": {"$gte": today},
            }
        ).sort("next_execution_date", 1).limit(10)
    )
    for r in recurring:
        r["_id"] = str(r["_id"])

    return Response(
        {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_savings": round(total_income - total_expenses, 2),
            "category_expenses": category_expenses,
            "goals": goals_data,
            "total_invested": round(total_invested, 2),
            "current_investment_value": round(total_current, 2),
            "investment_return": round(total_current - total_invested, 2),
            "upcoming_recurring": recurring,
        }
    )
