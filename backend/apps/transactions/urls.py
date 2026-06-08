from django.urls import path
from . import views

urlpatterns = [
    path("transactions/", views.transaction_list, name="transaction-list"),
    path("transactions/<str:transaction_id>/", views.transaction_detail, name="transaction-detail"),
    path("transactions/upload/", views.upload_file, name="transaction-upload"),
    path("health/", views.health_check, name="health-check"),
]
