from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("finance/<int:pk>/print/", views.print_finance_invoice, name="print_finance_invoice"),
]