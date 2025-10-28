from django.db import models
from contractor.models import Contractor
from workorder.models import ItemOrder
from decimal import Decimal
from django.utils.html import format_html
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class PaymentOrder(models.Model):
    """ Modelo de ordenes de pago """
    STATES = [
        ('in_progress', 'In progress'),
        ('done', 'Done'),
        ('canceled', 'Canceled'),
        ('pending', 'Pending'),
    ]
    job = models.CharField("Job", max_length=150)
    invoice = models.CharField("Invoice #", max_length=50)
    assigned_date = models.DateField("Assigned")
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    crew_start_date = models.DateField("Crew Start", blank=True, null=True)
    crew_end_date = models.DateField("Crew End", blank=True, null=True)
    items_order = models.ManyToManyField(ItemOrder, related_name="payment_orders", blank=True)
    state = models.CharField(max_length=20, choices=STATES, default='pending')

    def __str__(self):
        return f"Payment order - {self.contractor.name}"
    
    def total_order_cal(self):
        """Calcula el total según los ItemOrder asociados."""
        from price.models import Price  # Import diferido para evitar ciclos
        total = Decimal('0')
        contractor = self.contractor

        # Recorremos los items relacionados a la orden de pago
        for item in self.items_order.select_related("product", "work_order__company"):
            # Buscamos el precio por contractor
            price = Price.objects.filter(
                product=item.product,
                contractor=contractor
            ).first()

            if price:
                total += price.value * item.quantity

        return total
    
    def total_order(self):
        total_str = f"${self.total_order_cal():,.2f}"
        return format_html("<strong>{}</strong>", total_str)
    

@receiver(post_save, sender=PaymentOrder)
def create_finance_record(sender, instance, **kwargs):
    """
    Crea o actualiza un registro Finance cuando una PaymentOrder cambia a 'finished'.
    """
    if instance.state == 'done':
        # Importamos aquí para evitar la importación circular
        from finance.models import Finance
        from price.models import Price

        total = 0
        for item in instance.items_order.select_related("product"):
            price = Price.objects.filter(
                product=item.product,
                contractor=instance.contractor
            ).first()
            if price:
                total += float(price.value) * float(item.quantity)

        # Crea o actualiza el registro Finance asociado
        finance, created = Finance.objects.get_or_create(
            payment=instance,
            defaults={"type": False, "total": total},
        )
        if not created:
            finance.total = total
            finance.save()