from django.db import models
from django.contrib.auth.models import User
from events.models import Event
from django.utils import timezone


class Contract(models.Model):
    """Modèle pour les conventions/contrats"""
    
    TYPE_CHOICES = [
        ('SERVICE', 'Contrat de service'),
        ('PARTNERSHIP', 'Partenariat'),
        ('SPONSORSHIP', 'Sponsoring'),
        ('VENUE', 'Location de lieu'),
        ('SUPPLIER', 'Fournisseur'),
        ('OTHER', 'Autre'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('PENDING', 'En attente'),
        ('ACTIVE', 'Actif'),
        ('COMPLETED', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]
    
    contract_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de contrat"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Titre du contrat"
    )
    contract_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type de contrat"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contracts',
        verbose_name="Événement associé"
    )
    client_name = models.CharField(
        max_length=200,
        verbose_name="Nom du client/partenaire"
    )
    client_email = models.EmailField(
        verbose_name="Email du client"
    )
    client_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Téléphone du client"
    )
    client_address = models.TextField(
        blank=True,
        verbose_name="Adresse du client"
    )
    start_date = models.DateField(
        verbose_name="Date de début"
    )
    end_date = models.DateField(
        verbose_name="Date de fin"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Montant (TND)"
    )
    terms = models.TextField(
        verbose_name="Conditions du contrat"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name="Statut"
    )
    signed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de signature"
    )
    signed_by_client = models.BooleanField(
        default=False,
        verbose_name="Signé par le client"
    )
    signed_by_admin = models.BooleanField(
        default=False,
        verbose_name="Signé par l'administrateur"
    )
    client_signature = models.TextField(
        blank=True,
        verbose_name="Signature client (base64)"
    )
    admin_signature = models.TextField(
        blank=True,
        verbose_name="Signature admin (base64)"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_contracts',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"
    
    def __str__(self):
        return f"{self.contract_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.contract_number:
            self.contract_number = self.generate_contract_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_contract_number():
        """Générer un numéro de contrat unique"""
        prefix = 'CTR'
        year = timezone.now().year
        count = Contract.objects.filter(contract_number__startswith=f"{prefix}{year}").count() + 1
        return f"{prefix}{year}{count:05d}"
    
    def is_fully_signed(self):
        """Vérifier si le contrat est totalement signé"""
        return self.signed_by_client and self.signed_by_admin
    
    def activate(self):
        """Activer le contrat"""
        if self.is_fully_signed():
            self.status = 'ACTIVE'
            self.signed_date = timezone.now()
            self.save()
            return True
        return False
    
    def complete(self):
        """Marquer le contrat comme terminé"""
        self.status = 'COMPLETED'
        self.save()
    
    def cancel(self):
        """Annuler le contrat"""
        self.status = 'CANCELLED'
        self.save()
    
    def is_active(self):
        """Vérifier si le contrat est actif"""
        return self.status == 'ACTIVE'
    
    def is_expired(self):
        """Vérifier si le contrat est expiré"""
        return self.end_date < timezone.now().date() and self.status == 'ACTIVE'
