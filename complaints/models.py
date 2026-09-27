from django.db import models
from django.contrib.auth.models import User
from events.models import Event
from reservations.models import Reservation
from django.utils import timezone


class Complaint(models.Model):
    """Modèle pour les réclamations"""
    
    CATEGORY_CHOICES = [
        ('RESERVATION', 'Problème de réservation'),
        ('EVENT', 'Problème d\'événement'),
        ('PAYMENT', 'Problème de paiement'),
        ('SERVICE', 'Qualité de service'),
        ('TECHNICAL', 'Problème technique'),
        ('OTHER', 'Autre'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Basse'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Haute'),
        ('URGENT', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'Nouvelle'),
        ('IN_PROGRESS', 'En cours de traitement'),
        ('RESOLVED', 'Résolue'),
        ('CLOSED', 'Fermée'),
    ]
    
    # Informations de base
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    reservation = models.ForeignKey(
        Reservation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Réservation concernée"
    )
    event = models.ForeignKey(
        Event, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Événement concerné"
    )
    
    # Détails de la réclamation
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="Catégorie"
    )
    subject = models.CharField(max_length=200, verbose_name="Sujet")
    description = models.TextField(verbose_name="Description détaillée")
    
    # Gestion
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW',
        verbose_name="Statut"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
        verbose_name="Priorité"
    )
    
    # Réponse admin
    admin_response = models.TextField(
        blank=True,
        verbose_name="Réponse de l'administrateur"
    )
    responded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_responses',
        verbose_name="Répondu par"
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Répondu le"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mise à jour le")
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Résolue le"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Réclamation"
        verbose_name_plural = "Réclamations"
    
    def __str__(self):
        return f"{self.subject} - {self.user.username}"
    
    def mark_as_resolved(self):
        """Marquer la réclamation comme résolue"""
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.save()
    
    def is_pending(self):
        """Vérifier si la réclamation est en attente"""
        return self.status in ['NEW', 'IN_PROGRESS']
    
    def get_status_color(self):
        """Retourner la couleur selon le statut"""
        colors = {
            'NEW': '#fbbf24',  # Jaune
            'IN_PROGRESS': '#3b82f6',  # Bleu
            'RESOLVED': '#10b981',  # Vert
            'CLOSED': '#6b7280',  # Gris
        }
        return colors.get(self.status, '#6b7280')
    
    def get_priority_color(self):
        """Retourner la couleur selon la priorité"""
        colors = {
            'LOW': '#10b981',  # Vert
            'MEDIUM': '#fbbf24',  # Jaune
            'HIGH': '#f97316',  # Orange
            'URGENT': '#ef4444',  # Rouge
        }
        return colors.get(self.priority, '#6b7280')
