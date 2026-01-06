"""
Management command to automatically close date groups after their closing date.

Usage:
    python manage.py close_expired_votes

To run automatically:

Option 1 - Cron (simple):
    Add to crontab (crontab -e):
    0 0 * * * cd /path/to/project && /path/to/venv/bin/python manage.py close_expired_votes >> /var/log/django_close_votes.log 2>&1

Option 2 - Systemd Timer (recommended for production):
    See systemd/README.md for detailed instructions.
    Files are located in: systemd/bonptitloup-close-votes.service
                         systemd/bonptitloup-close-votes.timer
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import gettext as _
from voting.models import DateGroup


class Command(BaseCommand):
    help = _('Ferme automatiquement les groupes de dates dont la date de fermeture est passée')

    def handle(self, *args, **options):
        """Close date groups where the closing date has passed"""
        today = timezone.now().date()
        
        # Find all active date groups with a closing date that has passed
        expired_groups = DateGroup.objects.filter(
            status='active',
            vote_closing_date__isnull=False,
            vote_closing_date__lt=today
        )
        
        # Get list of groups before updating (since update() doesn't return objects)
        expired_groups_list = list(expired_groups.values('id', 'title', 'vote_closing_date'))
        count = len(expired_groups_list)
        
        if count > 0:
            # Update status to 'closed'
            expired_groups.update(status='closed')
            self.stdout.write(
                self.style.SUCCESS(
                    _('%(count)s groupe(s) de dates ont été fermé(s) automatiquement.') % {'count': count}
                )
            )
            
            # List the closed groups
            for group in expired_groups_list:
                self.stdout.write(
                    f"  - {group['title']} (fermeture: {group['vote_closing_date']})"
                )
        else:
            self.stdout.write(
                self.style.SUCCESS(_('Aucun groupe de dates à fermer.'))
            )

