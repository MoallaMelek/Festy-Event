from django.db import models
from django.contrib.auth.models import User
from reservations.models import Reservation
from django.utils import timezone
import random
import string


class Payment(models.Model):
    """Modèle pour les paiements"""
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Espèces'),
        ('CARD', 'Carte bancaire'),
        ('BANK_TRANSFER', 'Virement bancaire'),
        ('MOBILE', 'Paiement mobile'),
        ('CHEQUE', 'Chèque'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('COMPLETED', 'Complété'),
        ('FAILED', 'Échoué'),
        ('REFUNDED', 'Remboursé'),
    ]
    
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Réservation"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Montant"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Méthode de paiement"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        verbose_name="Statut"
    )
    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name="ID de transaction"
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de paiement"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
    
    def __str__(self):
        return f"Paiement {self.transaction_id} - {self.amount} TND"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        if self.status == 'COMPLETED' and not self.payment_date:
            self.payment_date = timezone.now()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_transaction_id():
        """Générer un ID de transaction unique"""
        prefix = 'TXN'
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}{timestamp}{random_str}"
    
    def mark_as_completed(self):
        """Marquer le paiement comme complété"""
        self.status = 'COMPLETED'
        self.payment_date = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Marquer le paiement comme échoué"""
        self.status = 'FAILED'
        self.save()
    
    def refund(self):
        """Rembourser le paiement"""
        self.status = 'REFUNDED'
        self.save()


class Invoice(models.Model):
    """Modèle pour les factures"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Brouillon'),
        ('ISSUED', 'Émise'),
        ('PAID', 'Payée'),
        ('CANCELLED', 'Annulée'),
    ]
    
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de facture"
    )
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='invoice',
        verbose_name="Réservation"
    )
    issued_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date d'émission"
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'échéance"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Montant total"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        verbose_name="Montant TVA"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        verbose_name="Montant remise"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT',
        verbose_name="Statut"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issued_date']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
    
    def __str__(self):
        return f"Facture {self.invoice_number} - {self.total_amount} TND"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_invoice_number():
        """Générer un numéro de facture unique"""
        prefix = 'INV'
        year = timezone.now().year
        count = Invoice.objects.filter(invoice_number__startswith=f"{prefix}{year}").count() + 1
        return f"{prefix}{year}{count:05d}"
    
    def calculate_total(self):
        """Calculer le montant total"""
        subtotal = self.reservation.total_price
        total = subtotal + self.tax_amount - self.discount_amount
        return total
    
    def mark_as_paid(self):
        """Marquer la facture comme payée"""
        self.status = 'PAID'
        self.save()
    
    def mark_as_issued(self):
        """Marquer la facture comme émise"""
        self.status = 'ISSUED'
        self.issued_date = timezone.now()
        self.save()
    
    def cancel(self):
        """Annuler la facture"""
        self.status = 'CANCELLED'
        self.save()
