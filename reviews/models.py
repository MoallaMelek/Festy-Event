from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Review(models.Model):
    """Système d'avis pour lieux, événements, etc."""
    # Utilisation de GenericForeignKey pour lier à n'importe quel modèle
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Auteur et contenu
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Note (1-5 étoiles)'
    )
    title = models.CharField(max_length=200, verbose_name='Titre de l\'avis')
    comment = models.TextField(verbose_name='Commentaire')
    
    # Critères détaillés (optionnel)
    cleanliness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name='Propreté'
    )
    service_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name='Service'
    )
    value_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name='Rapport qualité/prix'
    )
    location_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        verbose_name='Emplacement'
    )
    
    # Réactions
    helpful_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de "Utile"')
    
    # Modération
    is_verified = models.BooleanField(default=False, verbose_name='Avis vérifié')
    is_approved = models.BooleanField(default=True, verbose_name='Approuvé')
    admin_response = models.TextField(blank=True, verbose_name='Réponse de l\'admin')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-created_at']
        unique_together = ['content_type', 'object_id', 'author']
    
    def __str__(self):
        return f'{self.rating}★ - {self.title} par {self.author.username}'
    
    def get_average_criteria_rating(self):
        """Calcule la moyenne des critères détaillés"""
        ratings = [
            r for r in [
                self.cleanliness_rating,
                self.service_rating,
                self.value_rating,
                self.location_rating
            ] if r is not None
        ]
        return sum(ratings) / len(ratings) if ratings else self.rating


class ReviewHelpful(models.Model):
    """Indique si un utilisateur trouve un avis utile"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']
        verbose_name = 'Vote "Utile"'
        verbose_name_plural = 'Votes "Utile"'
    
    def __str__(self):
        return f'{self.user.username} trouve utile: {self.review.title}'


class FAQ(models.Model):
    """Questions fréquemment posées"""
    CATEGORY_CHOICES = [
        ('RESERVATION', 'Réservations'),
        ('PAYMENT', 'Paiements'),
        ('LOCATION', 'Lieux'),
        ('EVENT', 'Événements'),
        ('ACCOUNT', 'Compte'),
        ('GENERAL', 'Général'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    question = models.CharField(max_length=300, verbose_name='Question')
    answer = models.TextField(verbose_name='Réponse')
    order = models.IntegerField(default=0, verbose_name='Ordre d\'affichage')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de vues')
    helpful_count = models.PositiveIntegerField(default=0, verbose_name='Nombre de "Utile"')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['category', 'order', '-helpful_count']
    
    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    """Messages de contact"""
    STATUS_CHOICES = [
        ('NEW', 'Nouveau'),
        ('IN_PROGRESS', 'En cours'),
        ('RESOLVED', 'Résolu'),
        ('CLOSED', 'Fermé'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nom')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Téléphone')
    subject = models.CharField(max_length=200, verbose_name='Sujet')
    message = models.TextField(verbose_name='Message')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    admin_notes = models.TextField(blank=True, verbose_name='Notes admin')
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.subject} - {self.name}'
