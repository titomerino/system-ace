from django.contrib import admin
from django import forms
from django.utils.html import format_html
from workorder.models import ItemOrder, WorkOrder
from price.models import Price
from decimal import Decimal

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
        "total_price_display",
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
                # ("work_order",),# <- Campo virtual agregado
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
    
    def total_price_display(self, obj):
        """Calcula el total según los ItemOrder asociados."""
        total = Decimal('0')
        contractor = obj.contractor

        # Recorremos los items relacionados a la orden de pago
        for item in obj.items_order.select_related("product", "work_order__company"):
            # Buscamos el precio por contractor
            price = Price.objects.filter(
                product=item.product,
                contractor=contractor
            ).first()

            if price:
                total += price.value * item.quantity

        total_str = f"${total:,.2f}"
        return format_html("<strong>{}</strong>", total_str)
    
    
    def render_change_form(self, request, context, *args, **kwargs):
        """Agrega el total en la vista de detalle del PaymentOrder."""
        obj = context.get("original")
        if obj:
            total = self.total_price_display(obj)
            context["adminform"].form.fields["items_order"].help_text = f"💰 Total calculado: {total}"
        return super().render_change_form(request, context, *args, **kwargs)
 
    colored_state.short_description = "State"
    colored_state.admin_order_field = "state"
    total_price_display.short_description = "Total price"
    total_price_display.admin_order_field = "total_price_display"
