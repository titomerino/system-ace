from django.contrib import admin
from product.models import Product

# Register your models here.

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display =  ("name", "description")
    search_fields = ("name",)
    list_per_page = 12