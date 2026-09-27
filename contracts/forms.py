from django import forms
from .models import Contract


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = [
            'title',
            'contract_type',
            'event',
            'client_name',
            'client_email',
            'client_phone',
            'client_address',
            'start_date',
            'end_date',
            'amount',
            'terms',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Titre du contrat'}),
            'contract_type': forms.Select(),
            'event': forms.Select(),
            'client_name': forms.TextInput(attrs={'placeholder': 'Nom du client/partenaire'}),
            'client_email': forms.EmailInput(attrs={'placeholder': 'Email du client'}),
            'client_phone': forms.TextInput(attrs={'placeholder': 'Téléphone du client'}),
            'client_address': forms.Textarea(attrs={'placeholder': 'Adresse du client', 'rows': 2}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'placeholder': 'Montant en TND', 'step': '0.001'}),
            'terms': forms.Textarea(attrs={'placeholder': 'Termes et conditions du contrat', 'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make event optional
        self.fields['event'].required = False
        self.fields['client_phone'].required = False
        self.fields['client_address'].required = False
