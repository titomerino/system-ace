from django.db import models
from workorder.models import WorkOrder
from payment.models import PaymentOrder

# Create your models here.
class Finance(models.Model):
    """ Modelo para control de entradas y salidas """
    STATES = [
        (True, 'Income'),
        (False, 'outflow'),
    ]
    type = models.BooleanField(default=True, choices=STATES)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='work_order_finance'
    )
    payment = models.ForeignKey(
        PaymentOrder,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='payment_finance'
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(work_order__isnull=False) | models.Q(payment__isnull=False),
                name='finance_must_have_entity'
            )
        ]

    def __str__(self):
        if self.work_order:
            crew = self.work_order.crew or "No crew"
            company = getattr(self.work_order.company, "name", "No company")
            return f"{crew} — {company}"
        elif self.payment:
            job = self.payment.job or "No job"
            contractor = getattr(self.payment.contractor, "name", "No contractor")
            return f"{job} — {contractor}"
        return "Finance record"
