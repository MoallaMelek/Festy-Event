from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class BlogCategory(models.Model):
    """Catégories pour les articles de blog"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-folder', help_text='Classe FontAwesome')
    color = models.CharField(max_length=7, default='#fb923c', help_text='Code couleur hexadécimal')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Catégorie de blog'
        verbose_name_plural = 'Catégories de blog'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Articles de blog"""
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('PUBLISHED', 'Publié'),
        ('ARCHIVED', 'Archivé'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Titre')
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    
    # Contenu
    excerpt = models.TextField(max_length=300, verbose_name='Résumé', help_text='Court résumé pour l\'aperçu')
    content = models.TextField(verbose_name='Contenu')
    featured_image = models.URLField(blank=True, verbose_name='Image principale', help_text='URL de l\'image')
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    # Statut et publication
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_featured = models.BooleanField(default=False, verbose_name='Article à la une')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    
    # Tags
    tags = models.CharField(max_length=200, blank=True, help_text='Tags séparés par des virgules')
    
    # Dates
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Article de blog'
        verbose_name_plural = 'Articles de blog'
        ordering = ['-published_at', '-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Incrémenter le compteur de vues"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_tags_list(self):
        """Retourner la liste des tags"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class BlogComment(models.Model):
    """Commentaires sur les articles de blog"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(verbose_name='Commentaire')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    is_approved = models.BooleanField(default=True, verbose_name='Approuvé')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['created_at']
    
    def __str__(self):
        return f'Commentaire de {self.author.username} sur {self.post.title}'


class Newsletter(models.Model):
    """Inscription à la newsletter"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Abonné newsletter'
        verbose_name_plural = 'Abonnés newsletter'
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email
