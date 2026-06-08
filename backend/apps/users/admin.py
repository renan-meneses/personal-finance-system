from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "theme_preference", "monthly_income")
    search_fields = ("user__username",)


admin.site.register(UserProfile, UserProfileAdmin)
