from django.contrib import admin
from django import forms
from django.utils.html import format_html
from workorder.models import ItemOrder

from payment.models import PaymentOrder


# Register your models here.
class PaymentOrderAdminForm(forms.ModelForm):
    class Meta:
        model = PaymentOrder
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtener los ItemOrder que ya están asociados a otros PaymentOrders
        used_items = ItemOrder.objects.filter(payment_orders__isnull=False).distinct()

        # Mostrar solo los ItemOrder que no están en ningún PaymentOrder
        available_items = ItemOrder.objects.exclude(id__in=used_items)

        # Si estamos editando una instancia existente, mantener los items que ya tiene asignados
        if self.instance.pk:
            available_items = available_items | self.instance.items_order.all()

        # Asignar el queryset filtrado al campo
        self.fields["items_order"].queryset = available_items.distinct()




@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    form = PaymentOrderAdminForm
    list_display =  (
        "invoice",
        "job",
        "contractor__name",
        "assigned_date",
        "crew_start_date",
        "crew_end_date",
        "colored_state",
        "total_order",
    )
    list_filter = (
        "state",
    )
    filter_horizontal = ["items_order"]
    search_fields = ("invoice", "contractor__name", "job")
    fieldsets = (
        (None, {
            "fields": (
                ("job", "invoice"),
                ("assigned_date", "contractor"),
                ("crew_start_date", "crew_end_date"),
                ("items_order",),
                ("state",),
            ),
            "classes": ("wide",),
        }),
    )
    list_per_page = 12

    def colored_state(self, obj):
        """Show state with color badge."""
        colors = {
            'in_progress': '#3498db',  # blue
            'done': '#2ecc71',     # green
            'canceled': '#e74c3c',     # red
            'pending': '#f1c40f',      # yellow
        }
        color = colors.get(obj.state, '#95a5a6')  # default grey
        label = dict(PaymentOrder.STATES).get(obj.state, obj.state)
        return format_html(
            '<span style="background-color: {}; color: black; padding: 4px 8px; border-radius: 6px; font-weight: 500;">{}</span>',
            color,
            label,
        )
 
    colored_state.short_description = "State"
    colored_state.admin_order_field = "state"
