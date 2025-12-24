from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Child


class DateInput(forms.DateInput):
    """Custom DateInput widget that ensures proper format for HTML5 date inputs"""
    input_type = 'date'
    
    def format_value(self, value):
        """Format the date value as YYYY-MM-DD for HTML5 date input"""
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        # Format as YYYY-MM-DD
        return value.strftime('%Y-%m-%d')


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['first_name', 'last_name', 'birth_date']
        labels = {
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
            'birth_date': _('Date de naissance'),
        }
        widgets = {
            'birth_date': DateInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

