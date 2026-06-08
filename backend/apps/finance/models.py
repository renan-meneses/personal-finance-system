from django.db import models
from django.contrib.auth.models import User


class CategoryBudget(models.Model):
    CATEGORY_CHOICES = (
        ("housing", "Housing"),
        ("transport", "Transport"),
        ("food", "Food"),
        ("utilities", "Utilities"),
        ("entertainment", "Entertainment"),
        ("health", "Health"),
        ("education", "Education"),
        ("shopping", "Shopping"),
        ("salary", "Salary"),
        ("investment", "Investment"),
        ("transfer", "Transfer"),
        ("other", "Other"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    alert_80_sent = models.BooleanField(default=False)
    alert_100_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "category", "month", "year")
        verbose_name_plural = "Category budgets"

    @property
    def spend_percentage(self):
        if self.limit_amount == 0:
            return 0.0
        return float(self.current_spend / self.limit_amount) * 100

    @property
    def needs_alert_80(self):
        return self.spend_percentage >= 80 and not self.alert_80_sent

    @property
    def needs_alert_100(self):
        return self.spend_percentage >= 100 and not self.alert_100_sent

    def __str__(self):
        return f"{self.user.username} - {self.category} {self.month}/{self.year}"


class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="credit_cards")
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2)
    closing_day = models.PositiveSmallIntegerField()
    due_day = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class CreditCardStatement(models.Model):
    credit_card = models.ForeignKey(
        CreditCard, on_delete=models.CASCADE, related_name="statements"
    )
    closing_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-closing_date"]

    def __str__(self):
        return f"{self.credit_card.name} - {self.closing_date}"


class FinancialGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="goals")
    name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    current_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    target_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0.0
        return min(100.0, float(self.current_amount / self.target_amount) * 100)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class InvestmentPortfolio(models.Model):
    ASSET_TYPES = (
        ("fixed_income", "Fixed Income"),
        ("variable_income", "Variable Income"),
        ("real_estate", "Real Estate"),
        ("crypto", "Cryptocurrency"),
        ("other", "Other"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="investments"
    )
    asset_name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    quantity = models.DecimalField(max_digits=18, decimal_places=6)
    average_price = models.DecimalField(max_digits=15, decimal_places=2)
    current_price = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_invested(self):
        return float(self.quantity) * float(self.average_price)

    @property
    def current_value(self):
        return float(self.quantity) * float(self.current_price)

    @property
    def profit_loss(self):
        return self.current_value - self.total_invested

    @property
    def profit_loss_percentage(self):
        if self.total_invested == 0:
            return 0.0
        return (self.profit_loss / self.total_invested) * 100

    def __str__(self):
        return f"{self.asset_name} ({self.asset_type})"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"
