from django import forms
from .models import Event, EventRecommendation
from django.utils import timezone

class EventForm(forms.ModelForm):
    """Formulaire pour créer et modifier des événements"""
    
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        label="Date et heure",
        help_text="Sélectionnez la date et l'heure de l'événement"
    )
    
    class Meta:
        model = Event
        fields = [
            'title', 
            'description', 
            'category', 
            'date', 
            'location', 
            'capacity', 
            'price_per_person',
            'image_url',
            'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Concert de Jazz à Carthage'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Décrivez votre événement en détail...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Amphithéâtre de Carthage, Tunis'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Ex: 500'
            }),
            'price_per_person': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ex: 85.00'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://exemple.com/image.jpg (optionnel)'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def clean_date(self):
        """Vérifier que la date est dans le futur"""
        date = self.cleaned_data.get('date')
        if date and date < timezone.now():
            raise forms.ValidationError("La date de l'événement doit être dans le futur.")
        return date
    
    def clean_capacity(self):
        """Vérifier que la capacité est positive"""
        capacity = self.cleaned_data.get('capacity')
        if capacity and capacity < 1:
            raise forms.ValidationError("La capacité doit être au moins de 1 personne.")
        return capacity
    
    def clean_price_per_person(self):
        """Vérifier que le prix est positif"""
        price = self.cleaned_data.get('price_per_person')
        if price and price < 0:
            raise forms.ValidationError("Le prix ne peut pas être négatif.")
        return price
    
    def save(self, commit=True):
        """Surcharger save pour initialiser available_seats"""
        event = super().save(commit=False)
        
        # Si c'est un nouvel événement, initialiser available_seats
        if not event.pk:
            event.available_seats = event.capacity
        
        if commit:
            event.save()
        
        return event


class RecommendationForm(forms.ModelForm):
    """Formulaire pour créer et modifier des recommandations"""
    
    rating = forms.ChoiceField(
        choices=[(i, f'{i} étoile{"s" if i > 1 else ""}') for i in range(1, 6)],
        initial=5,
        widget=forms.Select(attrs={'class': 'form-control rating-select'}),
        label='Note générale'
    )
    organization_rating = forms.ChoiceField(
        choices=[(i, f'{i} ★') for i in range(1, 6)],
        initial=5,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Organisation'
    )
    ambiance_rating = forms.ChoiceField(
        choices=[(i, f'{i} ★') for i in range(1, 6)],
        initial=5,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Ambiance'
    )
    value_rating = forms.ChoiceField(
        choices=[(i, f'{i} ★') for i in range(1, 6)],
        initial=5,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Rapport qualité/prix'
    )
    venue_rating = forms.ChoiceField(
        choices=[(i, f'{i} ★') for i in range(1, 6)],
        initial=5,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Lieu/Emplacement'
    )
    
    class Meta:
        model = EventRecommendation
        fields = [
            'rating',
            'title',
            'comment',
            'organization_rating',
            'ambiance_rating',
            'value_rating',
            'venue_rating',
            'would_recommend',
            'tags',
            'photo_url',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Une soirée inoubliable !',
                'maxlength': '200'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Partagez votre expérience en détail...'
            }),
            'would_recommend': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'checked': 'checked'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: convivial, familial, professionnel'
            }),
            'photo_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://exemple.com/photo.jpg (optionnel)'
            }),
        }
        labels = {
            'title': 'Titre de votre recommandation',
            'comment': 'Votre avis détaillé',
            'would_recommend': 'Je recommande cet événement',
            'tags': 'Mots-clés (séparés par des virgules)',
            'photo_url': 'Photo (URL)',
        }
    
    def clean_title(self):
        """Valider le titre"""
        title = self.cleaned_data.get('title')
        if title and len(title) < 5:
            raise forms.ValidationError("Le titre doit contenir au moins 5 caractères.")
        return title
    
    def clean_comment(self):
        """Valider le commentaire"""
        comment = self.cleaned_data.get('comment')
        if comment and len(comment) < 20:
            raise forms.ValidationError("Votre avis doit contenir au moins 20 caractères pour être utile.")
        return comment
