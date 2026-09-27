from django import forms
from .models import Complaint
from reservations.models import Reservation
from events.models import Event


class ComplaintForm(forms.ModelForm):
    """Formulaire pour créer une réclamation"""
    
    class Meta:
        model = Complaint
        fields = ['category', 'subject', 'description', 'reservation', 'event']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Problème avec ma réservation'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Décrivez votre problème en détail...'
            }),
            'reservation': forms.Select(attrs={
                'class': 'form-control',
            }),
            'event': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Marquer les champs comme optionnels
        self.fields['reservation'].required = False
        self.fields['event'].required = False
        
        # Filtrer les réservations pour l'utilisateur connecté
        if user:
            self.fields['reservation'].queryset = Reservation.objects.filter(user=user)
            self.fields['reservation'].empty_label = "Sélectionner une réservation (optionnel)"
        else:
            self.fields['reservation'].queryset = Reservation.objects.none()
            
        # Tous les événements disponibles
        self.fields['event'].queryset = Event.objects.all()
        self.fields['event'].empty_label = "Sélectionner un événement (optionnel)"


class ComplaintResponseForm(forms.ModelForm):
    """Formulaire pour répondre à une réclamation (admin)"""
    
    class Meta:
        model = Complaint
        fields = ['admin_response', 'status', 'priority']
        widgets = {
            'admin_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Votre réponse à l\'utilisateur...'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control',
            }),
        }
