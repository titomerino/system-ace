from django.db import models
from company.models import Company
from product.models import Product

# Create your models here.
class WorkOrder(models.Model):
    """ Modelo de ordenes de trabajo """
    STATES = [
        ('in_progress', 'In progress'),
        ('finished', 'Finished'),
        ('canceled', 'Canceled'),
        ('pending', 'Pending'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    number_order = models.CharField("Order #", max_length=150)
    number_job = models.CharField("Job #", max_length=150)
    assigned_date = models.DateField("Assigned")
    crew = models.CharField("Crew", max_length=150)
    crew_start_date = models.DateField("Crew Start", blank=True, null=True)
    crew_end_date = models.DateField("Crew End", blank=True, null=True)
    address = models.TextField()
    instructions = models.TextField(blank=True, null=True)
    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATES, default='pending')
    products = models.ManyToManyField(Product, through='ItemOrder')

    def __str__(self):
        return f"Order {self.number_order} - {self.company.name}"
    

class ItemOrder(models.Model):
    """  """
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit = models.CharField("U/M", max_length=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ( {self.work_order.company.name} -- Order #{self.work_order.number_order})"
    