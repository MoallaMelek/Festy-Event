from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User

class Event(models.Model):
    """Modèle pour les événements"""
    
    CATEGORY_CHOICES = [
        ('MUSIQUE', 'Musique'),
        ('BUSINESS', 'Business'),
        ('GASTRONOMIE', 'Gastronomie'),
        ('SPORT', 'Sport'),
        ('CULTURE', 'Culture'),
    ]
    
    STATUS_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('EN_ATTENTE', 'En attente de validation'),
        ('CONFIRME', 'Confirmé'),
        ('ANNULE', 'Annulé'),
        ('TERMINE', 'Terminé'),
    ]
    
    # Informations de base
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="Catégorie"
    )
    
    # Date et lieu
    date = models.DateTimeField(verbose_name="Date et heure")
    location = models.CharField(max_length=200, verbose_name="Lieu")
    
    # Capacité et prix
    capacity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Capacité maximale"
    )
    available_seats = models.IntegerField(
        verbose_name="Places disponibles"
    )
    price_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix par personne (TND)"
    )
    
    # Statut et métadonnées
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EN_ATTENTE',
        verbose_name="Statut"
    )
    image_url = models.URLField(blank=True, verbose_name="URL de l'image")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date']
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.available_seats:
            self.available_seats = self.capacity
        super().save(*args, **kwargs)
    
    def is_available(self):
        """Vérifier si l'événement est disponible pour réservation"""
        return (
            self.status == 'CONFIRME' and 
            self.available_seats > 0 and 
            self.date > timezone.now()
        )
    
    def get_registered_count(self):
        """Obtenir le nombre de participants inscrits"""
        return self.capacity - self.available_seats
    
    def get_average_rating(self):
        """Obtenir la note moyenne de l'événement"""
        recommendations = self.recommendations.filter(is_approved=True)
        if recommendations.exists():
            return round(recommendations.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0
    
    def get_recommendations_count(self):
        """Obtenir le nombre de recommandations approuvées"""
        return self.recommendations.filter(is_approved=True).count()


class EventRecommendation(models.Model):
    """Recommandations et évaluations pour les événements"""
    
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='recommendations',
        verbose_name="Événement"
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='event_recommendations',
        verbose_name="Utilisateur"
    )
    
    # Note et commentaire
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note (1-5 étoiles)"
    )
    title = models.CharField(
        max_length=200, 
        verbose_name="Titre de la recommandation"
    )
    comment = models.TextField(verbose_name="Commentaire")
    
    # Critères détaillés
    organization_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Organisation"
    )
    ambiance_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Ambiance"
    )
    value_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Rapport qualité/prix"
    )
    venue_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Lieu/Emplacement"
    )
    
    # Recommandation
    would_recommend = models.BooleanField(
        default=True,
        verbose_name="Je recommande cet événement"
    )
    
    # Tags et catégories
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Mots-clés séparés par des virgules (ex: convivial, familial, professionnel)",
        verbose_name="Mots-clés"
    )
    
    # Réactions
    helpful_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Nombre de votes 'Utile'"
    )
    
    # Modération
    is_approved = models.BooleanField(
        default=True,
        verbose_name="Approuvé"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Mise en avant"
    )
    admin_response = models.TextField(
        blank=True,
        verbose_name="Réponse de l'administrateur"
    )
    
    # Photos (URLs)
    photo_url = models.URLField(
        blank=True,
        verbose_name="Photo (URL)"
    )
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Recommandation d'événement"
        verbose_name_plural = "Recommandations d'événements"
        unique_together = ['event', 'user']
    
    def __str__(self):
        return f"{self.rating}★ - {self.title} par {self.user.username}"
    
    def get_average_criteria_rating(self):
        """Calcule la moyenne des critères détaillés"""
        return round((
            self.organization_rating + 
            self.ambiance_rating + 
            self.value_rating + 
            self.venue_rating
        ) / 4, 1)
    
    def get_tags_list(self):
        """Retourne la liste des tags"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []


class RecommendationHelpful(models.Model):
    """Vote 'Utile' pour une recommandation"""
    
    recommendation = models.ForeignKey(
        EventRecommendation,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['recommendation', 'user']
        verbose_name = "Vote 'Utile'"
        verbose_name_plural = "Votes 'Utile'"
    
    def __str__(self):
        return f"{self.user.username} trouve utile: {self.recommendation.title}"
