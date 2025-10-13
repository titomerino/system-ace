from django.db import models

# Create your models here.
class Product(models.Model):
    """ Model de producto """
    name = models.CharField("Name", max_length=250)
    description  = models.TextField("Description")