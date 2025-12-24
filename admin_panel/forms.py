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
        fields = ['title', 'description', 'status']
        labels = {
            'title': _('Titre'),
            'description': _('Description'),
            'status': _('Statut'),
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
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
            }),
        }
        help_texts = {
            'content': _('Vous pouvez utiliser la syntaxe Markdown pour formater le texte. Exemples:\n'
                        '- # Titre\n'
                        '- **gras**\n'
                        '- *italique*\n'
                        '- [lien](url)\n'
                        '- - liste à puces'),
        }

