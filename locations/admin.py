from django.contrib import admin
from .models import Location, BlockedDate


class BlockedDateInline(admin.TabularInline):
    model = BlockedDate
    extra = 1
    fields = ['date', 'reason', 'notes']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'governorate', 'location_type', 'capacity', 'status']
    list_filter = ['status', 'location_type', 'governorate', 'city']
    search_fields = ['name', 'city', 'address']
    inlines = [BlockedDateInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'governorate', 'city', 'address', 'postal_code')
        }),
        ('Type et capacité', {
            'fields': ('location_type', 'capacity', 'area')
        }),
        ('Tarification', {
            'fields': ('hourly_rate', 'daily_rate')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Détails', {
            'fields': ('amenities', 'description')
        }),
        ('Contact', {
            'fields': ('contact_person', 'contact_phone', 'contact_email')
        }),
    )


@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ['location', 'date', 'reason', 'created_at']
    list_filter = ['reason', 'date']
    search_fields = ['location__name', 'notes']
    date_hierarchy = 'date'
