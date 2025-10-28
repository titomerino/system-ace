from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from company.models import Company
from product.models import Product
from django.utils.html import format_html

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
    invoice = models.CharField("Invoice", max_length=150)
    job = models.CharField("Job", max_length=150)
    assigned_date = models.DateField("Assigned")
    job_start_date = models.DateField("Job Start Date", blank=True, null=True)
    job_end_date = models.DateField("Job End Date", blank=True, null=True)
    address = models.TextField()
    instructions = models.TextField(blank=True, null=True)
    client_name = models.CharField(max_length=255)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    state = models.CharField(max_length=20, choices=STATES, default='pending')
    products = models.ManyToManyField(Product, through='ItemOrder')

    def __str__(self):
        return f"Order {self.invoice} - {self.company.name}"
    
    @property
    def items(self):
        return self.itemorder_set.select_related('product')
    
    def total_order_cal(self):
        """Calcula el total de la orden multiplicando cantidad * precio."""
        from price.models import Price  # Import diferido para evitar ciclos
        total = 0
        for item in self.itemorder_set.select_related("product"):
            price = Price.objects.filter(
                product=item.product,
                company=self.company
            ).first()
            if price:
                total += float(price.value) * float(item.quantity)
        return total
    
    def total_order(self):
        total_str = f"${self.total_order_cal():,.2f}"
        return format_html("<strong>{}</strong>", total_str)

class ItemOrder(models.Model):
    """  """
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit = models.CharField("U/M", max_length=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ( {self.work_order.company.name} -- Order #{self.work_order.invoice})"
    
    def get_price_company(self):
        """
        Obtiene el precio del producto según si el item pertenece a una WorkOrder (company)
        o está asociado indirectamente a una PaymentOrder (contractor).
        """
        from price.models import Price

        # 1️⃣ Si viene desde una orden de trabajo (WorkOrder)
        if self.work_order and self.work_order.company:
            price = Price.objects.filter(
                product=self.product,
                company=self.work_order.company
            ).first()
            if price:
                return float(price.value)

        return 0
    
    def get_price_contractor(self):
        from price.models import Price
        from payment.models import PaymentOrder
        
        payment = PaymentOrder.objects.filter(items_order=self).select_related('contractor').first()
        if payment and payment.contractor:
            price = Price.objects.filter(
                product=self.product,
                contractor=payment.contractor
            ).first()
            if price:
                return float(price.value)

        return 0
    
    def get_total_price_contractor(self):
        total = self.get_price_contractor()
        return float(total) * float(self.quantity)
    
    def get_total_price_company(self):
        total = self.get_price_company()
        return float(total) * float(self.quantity)

    
    def total(self):
        """Formato visual del total para el admin de work order"""
        total_val = self.get_price_company() * float(self.quantity)
        if not total_val:
            return "$0.00"
        total_str = "${:,.2f}".format(total_val)
        return format_html("<strong>{}</strong>", total_str)


@receiver(post_save, sender=WorkOrder)
def create_finance_record(sender, instance, **kwargs):
    """
    Crea o actualiza un registro Finance cuando una WorkOrder cambia a 'finished'.
    """
    if instance.state == 'finished':
        # Importamos aquí para evitar la importación circular
        from finance.models import Finance
        from price.models import Price

        total = 0
        for item in instance.itemorder_set.select_related("product"):
            price = Price.objects.filter(
                product=item.product,
                company=instance.company
            ).first()
            if price:
                total += float(price.value) * float(item.quantity)

        # Crea o actualiza el registro Finance asociado
        finance, created = Finance.objects.get_or_create(
            work_order=instance,
            defaults={"type": True, "total": total},
        )
        if not created:
            finance.total = total
            finance.save()
    