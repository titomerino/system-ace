from django.db import models
from contractor.models import Contractor
from django.core.exceptions import ValidationError

from company.models import Company
from product.models import Product

# Create your models here.
class Price(models.Model):
    """ Model de precio """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='prices'
    )
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='prices'
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(company__isnull=False) | models.Q(contractor__isnull=False),
                name='price_must_have_entity'
            )
        ]

    def clean(self):
        """Validación a nivel de modelo: evita duplicados"""
        if self.company_id:
            exists = Price.objects.filter(
                product=self.product,
                company_id=self.company_id
            ).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError(
                    f'A price for "{self.product.name}" already exists for the company {self.company}.'
                )

        if self.contractor_id:
            exists = Price.objects.filter(
                product=self.product, contractor=self.contractor
            ).exclude(pk=self.pk).exists()
            if exists:
                raise ValidationError(
                    f'A price for "{self.product.name}" already exists for the contractor {self.contractor}.'
                )

    def __str__(self):
        target = self.company if self.company else self.contractor
        return f"{target} - {self.product.name} : {self.value}"