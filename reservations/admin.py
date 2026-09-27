from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['reservation_code', 'user', 'event', 'number_of_seats', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at', 'is_paid']
    search_fields = ['reservation_code', 'user__username', 'event__title']
    readonly_fields = ['reservation_code', 'created_at', 'updated_at', 'cancelled_at']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('user', 'event', 'reservation_code')
        }),
        ('Détails de la réservation', {
            'fields': ('number_of_seats', 'status', 'total_price', 'is_paid', 'notes')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'cancelled_at')
        }),
    )
