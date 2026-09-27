from django import forms
from .models import Payment, Invoice
from reservations.models import Reservation
from decimal import Decimal


class PaymentForm(forms.ModelForm):
    """Formulaire pour enregistrer un paiement"""
    
    class Meta:
        model = Payment
        fields = ['reservation', 'amount', 'payment_method', 'notes']
        widgets = {
            'reservation': forms.Select(attrs={
                'class': 'form-control',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Montant en TND'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes supplémentaires...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer uniquement les réservations confirmées
        self.fields['reservation'].queryset = Reservation.objects.filter(status='CONFIRMED')
        self.fields['notes'].required = False


class InvoiceForm(forms.ModelForm):
    """Formulaire pour créer/modifier une facture"""
    
    class Meta:
        model = Invoice
        fields = ['reservation', 'total_amount', 'tax_amount', 'discount_amount', 'due_date', 'notes']
        widgets = {
            'reservation': forms.Select(attrs={
                'class': 'form-control',
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Montant total TND'
            }),
            'tax_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'TVA (19%)'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'placeholder': 'Remise'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes de la facture...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Réservations sans facture seulement
        self.fields['reservation'].queryset = Reservation.objects.filter(
            status='CONFIRMED'
        ).exclude(
            invoice__isnull=False
        )
        self.fields['due_date'].required = False
        self.fields['notes'].required = False
        
        # Calculer automatiquement à partir de la réservation si possible
        if 'reservation' in self.initial:
            reservation = self.initial['reservation']
            self.fields['total_amount'].initial = reservation.total_price
            self.fields['tax_amount'].initial = reservation.total_price * Decimal('0.19')
