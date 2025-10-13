from django.db import models


# Create your models here.
class Contractor(models.Model):
    """ Model de contratistas """
    name = models.CharField("Name", max_length=150)
    phone = models.CharField("Phone", max_length=15, blank=True, null=True)
    email = models.EmailField("Email", unique=True, blank=True, null=True)
    itin_ssn_ein = models.CharField("itin/ssn/ein", max_length=25)  

    def __str__(self):
        return self.name