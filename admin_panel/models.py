from django.db import models
from django.utils.translation import gettext_lazy as _


class WelcomePage(models.Model):
    """Model to store the welcome page content in Markdown format"""
    content = models.TextField(
        _('Contenu'),
        help_text=_('Contenu de la page d\'accueil en format Markdown'),
        default='# Bienvenue\n\nBienvenue sur le site des Bons P\'tits Loups !'
    )
    updated_at = models.DateTimeField(_('Mis à jour le'), auto_now=True)
    updated_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='welcome_pages_updated',
        verbose_name=_('Mis à jour par')
    )

    class Meta:
        verbose_name = _('Page d\'accueil')
        verbose_name_plural = _('Page d\'accueil')

    def __str__(self):
        return _('Page d\'accueil')

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get or create the single welcome page instance"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
