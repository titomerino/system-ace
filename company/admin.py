from django.contrib import admin
from company.models import Company

# Register your models here.
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    model = Company
    list_display =  (
        "name",
        "phone",
        "email",
        "contact",
    )