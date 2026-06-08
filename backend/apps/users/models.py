from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    THEME_CHOICES = (
        ("light", "Light"),
        ("dark", "Dark"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    theme_preference = models.CharField(
        max_length=5, choices=THEME_CHOICES, default="light"
    )
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"
