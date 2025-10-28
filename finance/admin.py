from django.contrib import admin
from finance.models import Finance
from django.utils.html import format_html

# Register your models here.
@admin.register(Finance)
class FinanceAdmin(admin.ModelAdmin):
    list_display = ("entity_info", "type", "colored_total", "print_invoice")

    def entity_info(self, obj):
        """Muestra datos según la relación existente"""
        if obj.work_order:
            job = obj.work_order.job or "—"
            company = getattr(obj.work_order.company, "name", "—")
            return f"{job} — {company}"
        elif obj.payment:
            job = obj.payment.job or "—"
            contractor = getattr(obj.payment.contractor, "name", "—")
            return f"{job} — {contractor}"
        return "—"

    def colored_total(self, obj):
        """Muestra el total con color según el tipo de movimiento."""
        color = "green" if obj.type else "red"
        try:
            total_value = float(obj.total)
            formatted_total = "${:,.2f}".format(total_value)
        except (TypeError, ValueError):
            formatted_total = "$0.00"

        return format_html('<strong style="color:{};">{}</strong>', color, formatted_total)
    
    def print_invoice(self, obj):
        url = f"/finance/finance/{obj.pk}/print/"
        return format_html(
            '<a class="button" href="{}" target="_blank" '
            'style="color:white;padding:3px 6px;border-radius:4px;text-decoration:none;">🖨️ Invoice</a>',
            url
        )

    print_invoice.short_description = "Print Invoice"
    entity_info.short_description = "Entidad (Job/Company o Job/Contractor)"
    colored_total.short_description = "Total"