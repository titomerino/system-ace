from django.shortcuts import get_object_or_404, render
from .models import Finance

def print_finance_invoice(request, pk):
    """Genera una vista de la factura usando template"""
    obj = get_object_or_404(Finance, pk=pk)
    
    if obj.work_order:
        return render(request, "finance/work_order_invoice.html", {"obj": obj})
    else:
        return render(request, "finance/payment_order_invoice.html", {"obj": obj})
