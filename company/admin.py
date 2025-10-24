from django.contrib import admin
from company.models import Company
from price.models import Price

# Register your models here.
class PriceInline(admin.TabularInline):
    model = Price
    extra = 1
    fields = ("product", "value")

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    inlines = [PriceInline]
    list_display =  (
        "name",
        "phone",
        "email",
        "contact",
    )
    list_per_page = 12
    search_fields = ("name",)
    fieldsets = (
        ('Information', {
            'fields': (
                ('name', 'contact'),
                ('email', 'phone'),
            ),
            'classes': ('wide',),
        }),
    )