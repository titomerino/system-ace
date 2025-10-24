from django.contrib import admin
from contractor.models import Contractor
from price.models import Price

# Register your models here.
class PriceInline(admin.TabularInline):
    model = Price
    extra = 1
    fields = ("product", "value")

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    inlines = [PriceInline]
    list_display =  ("name", "phone", "email", "itin_ssn_ein")
    search_fields = ("name",)
    list_per_page = 12
    fieldsets = (
        ('Personal information', {
            'fields': (
                ('name', 'itin_ssn_ein'),
                ('phone', 'email'),
            ),
            'classes': ('wide',),
        }),
    )