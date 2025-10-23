from django.db import models
from contractor.models import Contractor
from workorder.models import ItemOrder

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
    