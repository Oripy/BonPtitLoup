from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from .validators import validate_pin_code


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_("Adresse e-mail"))
    first_name = forms.CharField(max_length=30, required=True, label=_("Prénom"))
    last_name = forms.CharField(max_length=30, required=True, label=_("Nom"))
    
    password1 = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput,
        validators=[validate_pin_code],
        help_text=_("Entrez un code PIN de 4 à 8 chiffres.")
    )
    password2 = forms.CharField(
        label=_("Confirmation du mot de passe"),
        widget=forms.PasswordInput,
        help_text=_("Entrez le même code PIN pour confirmation.")
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Les deux mots de passe ne correspondent pas."))
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_parent = True  # All registrations are parents
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label=_("Nom d'utilisateur"))
    password = forms.CharField(widget=forms.PasswordInput, label=_("Mot de passe"))

