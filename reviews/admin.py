from django.contrib import admin
from django.utils.html import format_html
from .models import Review, ReviewHelpful, FAQ, ContactMessage


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'rating_stars', 'content_preview', 'is_verified', 'is_approved', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_verified', 'is_approved', 'created_at']
    search_fields = ['title', 'comment', 'author__username']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Informations de base', {
            'fields': ['author', 'content_type', 'object_id', 'title', 'comment']
        }),
        ('Évaluation', {
            'fields': ['rating', 'cleanliness_rating', 'service_rating', 'value_rating', 'location_rating']
        }),
        ('Modération', {
            'fields': ['is_verified', 'is_approved', 'admin_response', 'helpful_count']
        }),
    ]
    
    readonly_fields = ['helpful_count']
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        color = '#22c55e' if obj.rating >= 4 else '#fb923c' if obj.rating >= 3 else '#ef4444'
        return format_html('<span style="color: {}; font-size: 1.1rem;">{}</span>', color, stars)
    rating_stars.short_description = 'Note'
    
    def content_preview(self, obj):
        return obj.comment[:80] + '...' if len(obj.comment) > 80 else obj.comment
    content_preview.short_description = 'Aperçu'
    
    actions = ['approve_reviews', 'verify_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Approuver les avis sélectionnés'
    
    def verify_reviews(self, request, queryset):
        queryset.update(is_verified=True)
    verify_reviews.short_description = 'Marquer comme vérifiés'


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ['user', 'review', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'review__title']
    date_hierarchy = 'created_at'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'views_count', 'helpful_count']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
    
    fieldsets = [
        ('Question et réponse', {
            'fields': ['category', 'question', 'answer', 'order']
        }),
        ('Statistiques', {
            'fields': ['is_active', 'views_count', 'helpful_count'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['views_count', 'helpful_count']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'name', 'email', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Informations de contact', {
            'fields': ['name', 'email', 'phone', 'user']
        }),
        ('Message', {
            'fields': ['subject', 'message']
        }),
        ('Gestion', {
            'fields': ['status', 'admin_notes']
        }),
    ]
    
    readonly_fields = ['user']
    
    actions = ['mark_as_resolved', 'mark_as_in_progress']
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='RESOLVED')
    mark_as_resolved.short_description = 'Marquer comme résolu'
    
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='IN_PROGRESS')
    mark_as_in_progress.short_description = 'Marquer en cours'
