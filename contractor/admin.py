from django.contrib import admin
from contractor.models import Contractor

# Register your models here.
@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    model = Contractor
    list_display =  ("name", "phone", "email", "itin_ssn_ein")