from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

class UserRegistrationForm(UserCreationForm):
    """Formulaire d'inscription utilisateur - US 2.1"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur"
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email


class UserProfileForm(forms.ModelForm):
    """Formulaire de modification de profil - US 2.4"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Adresse email'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Vérifier si l'email existe déjà pour un autre utilisateur
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        return email


class UserDeleteForm(forms.Form):
    """Formulaire de confirmation de suppression de compte - US 2.5"""
    confirm = forms.BooleanField(
        required=True,
        label="Je confirme vouloir supprimer définitivement mon compte",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    password = forms.CharField(
        required=True,
        label="Mot de passe (pour confirmer)",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre mot de passe'
        })
    )
