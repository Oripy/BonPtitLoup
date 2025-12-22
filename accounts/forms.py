from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label=_("Adresse e-mail"))
    first_name = forms.CharField(max_length=30, required=True, label=_("Prénom"))
    last_name = forms.CharField(max_length=30, required=True, label=_("Nom"))
    role = forms.ChoiceField(
        choices=[('parent', _('Parent')), ('admin', _('Administrateur'))],
        required=True,
        widget=forms.RadioSelect,
        label=_("Rôle")
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        role = self.cleaned_data['role']
        if role == 'parent':
            user.is_parent = True
        elif role == 'admin':
            user.is_admin = True
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label=_("Nom d'utilisateur"))
    password = forms.CharField(widget=forms.PasswordInput, label=_("Mot de passe"))

