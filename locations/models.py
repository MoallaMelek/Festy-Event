from django.db import models
from django.contrib.auth.models import User


class Location(models.Model):
    """Modèle pour les lieux/salles d'événements"""
    
    TYPE_CHOICES = [
        ('INDOOR', 'Intérieur'),
        ('OUTDOOR', 'Extérieur'),
        ('HYBRID', 'Hybride'),
    ]
    
    STATUS_CHOICES = [
        ('AVAILABLE', 'Disponible'),
        ('OCCUPIED', 'Occupé'),
        ('MAINTENANCE', 'En maintenance'),
        ('UNAVAILABLE', 'Indisponible'),
    ]
    
    GOVERNORATE_CHOICES = [
        ('TUNIS', 'Tunis'),
        ('ARIANA', 'Ariana'),
        ('BEN_AROUS', 'Ben Arous'),
        ('MANOUBA', 'Manouba'),
        ('NABEUL', 'Nabeul'),
        ('ZAGHOUAN', 'Zaghouan'),
        ('BIZERTE', 'Bizerte'),
        ('BEJA', 'Béja'),
        ('JENDOUBA', 'Jendouba'),
        ('KEF', 'Le Kef'),
        ('SILIANA', 'Siliana'),
        ('SOUSSE', 'Sousse'),
        ('MONASTIR', 'Monastir'),
        ('MAHDIA', 'Mahdia'),
        ('SFAX', 'Sfax'),
        ('KAIROUAN', 'Kairouan'),
        ('KASSERINE', 'Kasserine'),
        ('SIDI_BOUZID', 'Sidi Bouzid'),
        ('GABES', 'Gabès'),
        ('MEDENINE', 'Médenine'),
        ('TATAOUINE', 'Tataouine'),
        ('GAFSA', 'Gafsa'),
        ('TOZEUR', 'Tozeur'),
        ('KEBILI', 'Kébili'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name="Nom du lieu"
    )
    address = models.TextField(
        verbose_name="Adresse"
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Ville"
    )
    governorate = models.CharField(
        max_length=20,
        choices=GOVERNORATE_CHOICES,
        default='TUNIS',
        verbose_name="Gouvernorat"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Code postal"
    )
    location_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='INDOOR',
        verbose_name="Type de lieu"
    )
    capacity = models.PositiveIntegerField(
        verbose_name="Capacité maximale"
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Surface (m²)"
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Tarif horaire (TND)"
    )
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Tarif journalier (TND)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE',
        verbose_name="Statut"
    )
    amenities = models.TextField(
        blank=True,
        verbose_name="Équipements disponibles"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )
    contact_person = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Personne de contact"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone de contact"
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name="Email de contact"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_locations',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Lieu"
        verbose_name_plural = "Lieux"
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    def is_available(self):
        """Vérifier si le lieu est disponible"""
        return self.status == 'AVAILABLE'
    
    def mark_as_occupied(self):
        """Marquer comme occupé"""
        self.status = 'OCCUPIED'
        self.save()
    
    def mark_as_available(self):
        """Marquer comme disponible"""
        self.status = 'AVAILABLE'
        self.save()
    
    def mark_as_maintenance(self):
        """Mettre en maintenance"""
        self.status = 'MAINTENANCE'
        self.save()


class BlockedDate(models.Model):
    """Dates bloquées pour un lieu spécifique"""
    
    REASON_CHOICES = [
        ('MAINTENANCE', 'Maintenance'),
        ('PRIVATE_EVENT', 'Événement privé'),
        ('RENOVATION', 'Rénovation'),
        ('HOLIDAY', 'Jour férié'),
        ('OTHER', 'Autre'),
    ]
    
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='blocked_dates',
        verbose_name="Lieu"
    )
    date = models.DateField(
        verbose_name="Date bloquée"
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        default='OTHER',
        verbose_name="Raison"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date']
        verbose_name = "Date bloquée"
        verbose_name_plural = "Dates bloquées"
        unique_together = ['location', 'date']
    
    def __str__(self):
        return f"{self.location.name} - {self.date.strftime('%d/%m/%Y')}"


