from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Child


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'birth_date']
        labels = {
            'name': _('Nom'),
            'birth_date': _('Date de naissance'),
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

