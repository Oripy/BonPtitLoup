from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    is_parent = models.BooleanField(default=False, verbose_name=_('Parent'))
    is_admin = models.BooleanField(default=False, verbose_name=_('Administrateur'))
    
    class Meta:
        verbose_name = _('Utilisateur')
        verbose_name_plural = _('Utilisateurs')

    def __str__(self):
        return self.username
