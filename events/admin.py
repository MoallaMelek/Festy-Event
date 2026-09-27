from django.contrib import admin
from .models import Event, EventRecommendation, RecommendationHelpful

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'category', 'status', 'available_seats', 'capacity', 'price_per_person']
    list_filter = ['status', 'category', 'date']
    search_fields = ['title', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('title', 'description', 'category', 'status')
        }),
        ('Date et lieu', {
            'fields': ('date', 'location')
        }),
        ('Capacité et tarification', {
            'fields': ('capacity', 'available_seats', 'price_per_person')
        }),
        ('Média', {
            'fields': ('image_url',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EventRecommendation)
class EventRecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'user', 'rating', 'is_approved', 'is_featured', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_featured', 'would_recommend', 'created_at']
    search_fields = ['title', 'comment', 'user__username', 'event__title', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'helpful_count']
    list_editable = ['is_approved', 'is_featured']
    
    fieldsets = (
        ('Informations', {
            'fields': ('event', 'user', 'title', 'rating')
        }),
        ('Commentaire', {
            'fields': ('comment', 'would_recommend', 'tags')
        }),
        ('Critères détaillés', {
            'fields': ('organization_rating', 'ambiance_rating', 'value_rating', 'venue_rating')
        }),
        ('Modération', {
            'fields': ('is_approved', 'is_featured', 'admin_response')
        }),
        ('Média', {
            'fields': ('photo_url',)
        }),
        ('Statistiques', {
            'fields': ('helpful_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RecommendationHelpful)
class RecommendationHelpfulAdmin(admin.ModelAdmin):
    list_display = ['recommendation', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['recommendation__title', 'user__username']

