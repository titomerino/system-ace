from django.contrib import admin
from workorder.models import WorkOrder, ItemOrder
from price.models import Price
from django.utils.html import format_html

# Register your models here.
class ItemOrderInline(admin.TabularInline):
    model = ItemOrder
    extra = 1
    search_fields = ["name", "product__name"]


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    inlines = [ItemOrderInline]
    list_display =  (
        "display_order",
        "client_name",
        "assigned_date",
        "crew_start_date",
        "crew_end_date",
        "colored_state",
        "total_price_display",
    )
    list_filter = (
        "state",
    )
    search_fields = ("client_name", "number_order", "number_job")
    fieldsets = (
        ('Order', {
            'fields': (
                ('company',),
                ('number_job', 'number_order'),
                ('crew', 'state'),
                ('assigned_date',),
                ('crew_start_date',),
                ('crew_end_date',),
            ),
            'classes': ('wide',),
        }),
        ('Client', {
            'fields': (
                ('client_name', 'client_phone'),
                ('client_email',),
                ('address', 'instructions',),
            ),
            'classes': ('wide',),
        })
    )

    def colored_state(self, obj):
        """Show state with color badge."""
        colors = {
            'in_progress': '#3498db',  # blue
            'finished': '#2ecc71',     # green
            'canceled': '#e74c3c',     # red
            'pending': '#f1c40f',      # yellow
        }
        color = colors.get(obj.state, '#95a5a6')  # default grey
        label = dict(WorkOrder.STATES).get(obj.state, obj.state)
        return format_html(
            '<span style="background-color: {}; color: black; padding: 4px 8px; border-radius: 6px; font-weight: 500;">{}</span>',
            color,
            label,
        )


    def display_order(self, obj):
        return str(obj)
    
    
    def total_price_display(self, obj):
        """Calcula el total de la orden basado en los precios asociados a los productos."""
        # Obtenemos los productos de la orden
        items = ItemOrder.objects.filter(work_order=obj)

        total = 0
        for item in items:
            price = Price.objects.filter(
                product=item.product,
                company=obj.company
            ).first()

            if price:
                total += float(price.value) * float(item.quantity)

        total_str = f"${total:,.2f}"
        return format_html("<strong>{}</strong>", total_str)

    colored_state.short_description = "State"
    colored_state.admin_order_field = "state"
    display_order.short_description = "Order" 
    total_price_display.short_description = "Total price"
    total_price_display.admin_order_field = "total_price_display"