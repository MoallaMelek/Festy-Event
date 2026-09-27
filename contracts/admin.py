from django.contrib import admin
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'title', 'contract_type', 'client_name', 'amount', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'contract_type', 'start_date']
    search_fields = ['contract_number', 'title', 'client_name', 'client_email']
    readonly_fields = ['created_at', 'updated_at', 'contract_number']
