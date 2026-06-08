from django.urls import path
from . import views

urlpatterns = [
    path("auth/login/", views.login_view, name="auth-login"),
    path("auth/logout/", views.logout_view, name="auth-logout"),
    path("profile/", views.profile_view, name="user-profile"),
    path("profile/theme/", views.theme_view, name="user-theme"),
]
