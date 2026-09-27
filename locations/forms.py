from django import forms
from .models import Location


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            'name',
            'governorate',
            'city',
            'address',
            'postal_code',
            'location_type',
            'capacity',
            'area',
            'hourly_rate',
            'daily_rate',
            'amenities',
            'contact_person',
            'contact_phone',
            'contact_email',
            'description',
            'status',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nom du lieu'}),
            'governorate': forms.Select(),
            'address': forms.TextInput(attrs={'placeholder': 'Adresse complète'}),
            'city': forms.TextInput(attrs={'placeholder': 'Ville'}),
            'postal_code': forms.TextInput(attrs={'placeholder': 'Code postal'}),
            'location_type': forms.Select(),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Capacité maximale'}),
            'area': forms.NumberInput(attrs={'placeholder': 'Surface en m²', 'step': '0.01'}),
            'hourly_rate': forms.NumberInput(attrs={'placeholder': 'Tarif horaire en TND', 'step': '0.001'}),
            'daily_rate': forms.NumberInput(attrs={'placeholder': 'Tarif journalier en TND', 'step': '0.001'}),
            'amenities': forms.Textarea(attrs={'placeholder': 'Équipements disponibles (un par ligne)', 'rows': 4}),
            'contact_person': forms.TextInput(attrs={'placeholder': 'Nom du contact'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'Téléphone'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description détaillée du lieu', 'rows': 4}),
            'status': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['postal_code'].required = False
        self.fields['area'].required = False
        self.fields['hourly_rate'].required = False
        self.fields['daily_rate'].required = False
        self.fields['amenities'].required = False
        self.fields['contact_person'].required = False
        self.fields['contact_phone'].required = False
        self.fields['contact_email'].required = False
        self.fields['description'].required = False
