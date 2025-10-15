from django.db import models


# Create your models here
class Company(models.Model):
    """ Model de compañias """
    name = models.CharField("Name", max_length=150)
    phone = models.CharField("Phone", max_length=15, blank=True, null=True)
    email = models.EmailField("Email", unique=True, blank=True, null=True)
    contact = models.CharField("Contact", max_length=150)
    address = models.TextField("Address", blank=True, null=True)
    other  = models.TextField("Other")

    def __str__(self):
        return self.name
    