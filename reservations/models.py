from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from events.models import Event
import uuid

class Reservation(models.Model):
    """
    Modèle pour gérer les réservations d'événements
    User Stories : 3.1, 3.2, 3.3
    """
    
    STATUS_CHOICES = [
        ('CONFIRMEE', 'Confirmée'),
        ('EN_ATTENTE', 'En attente'),
        ('ANNULEE', 'Annulée'),
    ]
    
    # Relations
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reservations',
        verbose_name="Participant"
    )
    event = models.ForeignKey(
        Event, 
        on_delete=models.CASCADE, 
        related_name='reservations',
        verbose_name="Événement"
    )
    
    # Informations de réservation
    number_of_seats = models.IntegerField(
        verbose_name="Nombre de places",
        validators=[MinValueValidator(1)],
        default=1
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CONFIRMEE',
        verbose_name="Statut"
    )
    
    # Prix et paiement
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix total (TND)",
        null=True,
        blank=True
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name="Payé"
    )
    
    # Métadonnées
    reservation_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Code de réservation"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifiée le")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Annulée le")
    
    # Notes additionnelles
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['event', 'status']),
        ]
    
    def __str__(self):
        return f"{self.reservation_code} - {self.user.username} - {self.event.title}"
    
    def save(self, *args, **kwargs):
        # Générer un code de réservation unique
        if not self.reservation_code:
            self.reservation_code = f"RES-{uuid.uuid4().hex[:10].upper()}"
        
        # Calculer le prix total
        if not self.total_price and self.event:
            self.total_price = self.event.price_per_person * self.number_of_seats
        
        super().save(*args, **kwargs)
    
    def cancel(self):
        """User Story 3.3 : Annuler une réservation"""
        if self.status != 'ANNULEE':
            self.status = 'ANNULEE'
            self.cancelled_at = timezone.now()
            self.save()
            
            # Libérer les places dans l'événement
            self.event.available_seats += self.number_of_seats
            self.event.save()
    
    def can_be_cancelled(self):
        """Vérifier si la réservation peut être annulée"""
        if self.status == 'ANNULEE':
            return False
        # Peut annuler jusqu'à 24h avant l'événement
        return self.event.date > timezone.now()
