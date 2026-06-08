from rest_framework import serializers
from .models import (
    CategoryBudget, CreditCard, CreditCardStatement,
    FinancialGoal, InvestmentPortfolio, Notification,
)


class CategoryBudgetSerializer(serializers.ModelSerializer):
    spend_percentage = serializers.ReadOnlyField()

    class Meta:
        model = CategoryBudget
        fields = (
            "id", "category", "limit_amount", "current_spend",
            "month", "year", "spend_percentage",
            "alert_80_sent", "alert_100_sent", "created_at",
        )
        read_only_fields = ("current_spend", "alert_80_sent", "alert_100_sent")


class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = "__all__"
        read_only_fields = ("user",)


class CreditCardStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCardStatement
        fields = "__all__"
        read_only_fields = ("credit_card",)


class FinancialGoalSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = FinancialGoal
        fields = (
            "id", "name", "target_amount", "current_amount",
            "target_date", "is_completed", "progress_percentage",
            "created_at", "updated_at",
        )
        read_only_fields = ("user",)


class InvestmentPortfolioSerializer(serializers.ModelSerializer):
    total_invested = serializers.ReadOnlyField()
    current_value = serializers.ReadOnlyField()
    profit_loss = serializers.ReadOnlyField()
    profit_loss_percentage = serializers.ReadOnlyField()

    class Meta:
        model = InvestmentPortfolio
        fields = (
            "id", "asset_name", "asset_type", "quantity",
            "average_price", "current_price", "total_invested",
            "current_value", "profit_loss", "profit_loss_percentage",
            "created_at", "updated_at",
        )
        read_only_fields = ("user",)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ("user",)
