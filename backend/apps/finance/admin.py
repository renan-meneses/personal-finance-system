from django.contrib import admin
from .models import CategoryBudget, CreditCard, CreditCardStatement, FinancialGoal, InvestmentPortfolio, Notification


class CategoryBudgetAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "limit_amount", "current_spend", "month", "year")
    list_filter = ("category", "month", "year")
    search_fields = ("user__username",)


class CreditCardAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "user", "credit_limit", "closing_day", "due_day")
    search_fields = ("name", "user__username")


class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "target_amount", "current_amount", "is_completed")
    list_filter = ("is_completed",)


class InvestmentPortfolioAdmin(admin.ModelAdmin):
    list_display = ("asset_name", "asset_type", "user", "quantity", "current_price")
    list_filter = ("asset_type",)


admin.site.register(CategoryBudget, CategoryBudgetAdmin)
admin.site.register(CreditCard, CreditCardAdmin)
admin.site.register(CreditCardStatement)
admin.site.register(FinancialGoal, FinancialGoalAdmin)
admin.site.register(InvestmentPortfolio, InvestmentPortfolioAdmin)
admin.site.register(Notification)
