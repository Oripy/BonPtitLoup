from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_pin_code(value):
    """Validate that password is a 4-8 digit PIN code"""
    if not value.isdigit():
        raise ValidationError(
            _('Le mot de passe doit contenir uniquement des chiffres.'),
            code='password_not_numeric',
        )
    if len(value) < 4:
        raise ValidationError(
            _('Le mot de passe doit contenir au moins 4 chiffres.'),
            code='password_too_short',
        )
    if len(value) > 8:
        raise ValidationError(
            _('Le mot de passe doit contenir au maximum 8 chiffres.'),
            code='password_too_long',
        )

