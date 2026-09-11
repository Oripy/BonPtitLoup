from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from voting.models import DateGroup, DateOption
from .models import WelcomePage


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


class DateGroupForm(forms.ModelForm):
    class Meta:
        model = DateGroup
        fields = [
            'title', 'description', 'status', 'vote_closing_date',
            'restrict_children_under_6', 'max_children_under_6',
            'restrict_children_over_6', 'max_children_over_6',
            'restrict_total_children', 'max_total_children'
        ]
        labels = {
            'title': _('Titre'),
            'description': _('Description'),
            'status': _('Statut'),
            'vote_closing_date': _('Date de fermeture des votes'),
            'restrict_children_under_6': _('Limiter le nombre d\'enfants de moins de 6 ans'),
            'max_children_under_6': _('Nombre maximum d\'enfants < 6 ans'),
            'restrict_children_over_6': _('Limiter le nombre d\'enfants de 6 ans ou plus'),
            'max_children_over_6': _('Nombre maximum d\'enfants >= 6 ans'),
            'restrict_total_children': _('Limiter le nombre total d\'enfants'),
            'max_total_children': _('Nombre maximum total d\'enfants'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'vote_closing_date': DateInput(attrs={'class': 'form-control'}),
            'restrict_children_under_6': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_children_under_6': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'restrict_children_over_6': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_children_over_6': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'restrict_total_children': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'max_total_children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class DateOptionForm(forms.ModelForm):
    class Meta:
        model = DateOption
        fields = ['date']
        labels = {
            'date': _('Date'),
        }
        widgets = {
            'date': DateInput(attrs={'class': 'form-control'}),
        }


DateOptionFormSet = inlineformset_factory(
    DateGroup,
    DateOption,
    form=DateOptionForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class WelcomePageForm(forms.ModelForm):
    class Meta:
        model = WelcomePage
        fields = ['content']
        labels = {
            'content': _('Contenu (Markdown)'),
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 20,
                'placeholder': _('Entrez le contenu en format Markdown...')
            })
        }

