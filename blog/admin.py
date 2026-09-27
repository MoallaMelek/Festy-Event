from django.contrib import admin
from django.utils.html import format_html
from .models import BlogCategory, BlogPost, BlogComment, Newsletter


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'posts_count', 'color_preview', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    
    def posts_count(self, obj):
        count = obj.posts.filter(status='PUBLISHED').count()
        return format_html('<span style="background: #fb923c; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-weight: 600;">{}</span>', count)
    posts_count.short_description = 'Articles publiés'
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px; background: {}; border-radius: 4px; border: 2px solid #e5e7eb;"></div>',
            obj.color
        )
    color_preview.short_description = 'Couleur'


class BlogCommentInline(admin.TabularInline):
    model = BlogComment
    extra = 0
    fields = ['author', 'content', 'is_approved', 'created_at']
    readonly_fields = ['created_at']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'views_count', 'comments_count', 'published_at']
    list_filter = ['status', 'category', 'is_featured', 'published_at']
    search_fields = ['title', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    inlines = [BlogCommentInline]
    
    fieldsets = [
        ('Informations de base', {
            'fields': ['title', 'slug', 'author', 'category', 'status', 'is_featured']
        }),
        ('Contenu', {
            'fields': ['excerpt', 'content', 'featured_image', 'tags']
        }),
        ('SEO', {
            'fields': ['meta_description', 'meta_keywords'],
            'classes': ['collapse']
        }),
        ('Statistiques', {
            'fields': ['views_count', 'published_at'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['views_count']
    
    def comments_count(self, obj):
        count = obj.comments.filter(is_approved=True).count()
        return format_html('<span style="color: #3b82f6; font-weight: 600;">{} 💬</span>', count)
    comments_count.short_description = 'Commentaires'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une nouvelle création
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'content_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author__username', 'content', 'post__title']
    date_hierarchy = 'created_at'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Aperçu'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'subscribed_at', 'unsubscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    date_hierarchy = 'subscribed_at'
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True, unsubscribed_at=None)
    activate_subscriptions.short_description = 'Activer les abonnements sélectionnés'
    
    def deactivate_subscriptions(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_active=False, unsubscribed_at=timezone.now())
    deactivate_subscriptions.short_description = 'Désactiver les abonnements sélectionnés'
