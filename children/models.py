from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import date


class Child(models.Model):
    first_name = models.CharField(max_length=100, verbose_name=_('Prénom'))
    last_name = models.CharField(max_length=100, verbose_name=_('Nom'))
    birth_date = models.DateField(verbose_name=_('Date de naissance'))
    parent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='children', verbose_name=_('Parent'))

    class Meta:
        verbose_name = _('Enfant')
        verbose_name_plural = _('Enfants')
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def age(self):
        """Calculate age in years"""
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
