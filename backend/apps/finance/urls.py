from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"budgets", views.CategoryBudgetViewSet, basename="budget")
router.register(r"credit-cards", views.CreditCardViewSet, basename="credit-card")
router.register(
    r"credit-card-statements",
    views.CreditCardStatementViewSet,
    basename="credit-card-statement",
)
router.register(r"goals", views.FinancialGoalViewSet, basename="goal")
router.register(r"investments", views.InvestmentPortfolioViewSet, basename="investment")
router.register(r"notifications", views.NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
    path("cash-flow/", views.cash_flow_projection, name="cash-flow"),
    path("dashboard/", views.dashboard_summary, name="dashboard-summary"),
]
