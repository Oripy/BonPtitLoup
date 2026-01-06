from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DateGroup(models.Model):
    STATUS_CHOICES = [
        ('active', _('Actif')),
        ('closed', _('Fermé')),
        ('inactive', _('Inactif')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Titre'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_date_groups', verbose_name=_('Créé par'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Date de création'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name=_('Statut'))
    vote_closing_date = models.DateField(blank=True, null=True, verbose_name=_('Date de fermeture des votes'))
    
    class Meta:
        verbose_name = _('Groupe de dates')
        verbose_name_plural = _('Groupes de dates')
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def is_closed(self):
        """Check if the date group is closed"""
        return self.status == 'closed'
    
    def is_inactive(self):
        """Check if the date group is inactive"""
        return self.status == 'inactive'
    
    def can_vote(self):
        """Check if voting is allowed for this date group"""
        from django.utils import timezone
        
        # Must be active status
        if self.status != 'active':
            return False
        
        # If closing date is set, check if it has passed
        if self.vote_closing_date:
            today = timezone.now().date()
            if today > self.vote_closing_date:
                return False
        
        return True

    def get_total_votes(self):
        """Get total number of votes for this date group"""
        # Use string reference to avoid circular import
        from django.apps import apps
        Vote = apps.get_model('voting', 'Vote')
        return Vote.objects.filter(time_slot__date_option__date_group=self).count()

    def get_vote_statistics(self):
        """Get voting statistics for all date options and time slots in this group"""
        stats = []
        for option in self.date_options.all():
            for time_slot in option.time_slots.all():
                yes_votes = time_slot.votes.filter(choice='yes').select_related('child')
                no_votes = time_slot.votes.filter(choice='no').select_related('child')
                maybe_votes = time_slot.votes.filter(choice='maybe').select_related('child')
                
                yes_count = yes_votes.count()
                no_count = no_votes.count()
                maybe_count = maybe_votes.count()
                total = yes_count + no_count + maybe_count
                
                stats.append({
                    'option': option,
                    'time_slot': time_slot,
                    'yes': yes_count,
                    'no': no_count,
                    'maybe': maybe_count,
                    'total': total,
                    'yes_percent': (yes_count / total * 100) if total > 0 else 0,
                    'no_percent': (no_count / total * 100) if total > 0 else 0,
                    'maybe_percent': (maybe_count / total * 100) if total > 0 else 0,
                    'yes_children': [str(vote.child) for vote in yes_votes.order_by('child__last_name', 'child__first_name')],
                    'no_children': [str(vote.child) for vote in no_votes.order_by('child__last_name', 'child__first_name')],
                    'maybe_children': [str(vote.child) for vote in maybe_votes.order_by('child__last_name', 'child__first_name')],
                })
        return stats


class DateOption(models.Model):
    date_group = models.ForeignKey(DateGroup, on_delete=models.CASCADE, related_name='date_options', verbose_name=_('Groupe de dates'))
    date = models.DateField(verbose_name=_('Date'))
    
    class Meta:
        verbose_name = _('Option de date')
        verbose_name_plural = _('Options de dates')
        ordering = ['date']

    def __str__(self):
        return str(self.date)
    
    def save(self, *args, **kwargs):
        """Override save to automatically create time slots"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Create default time slots for new date option
            TimeSlot.objects.get_or_create(date_option=self, period='morning')
            TimeSlot.objects.get_or_create(date_option=self, period='lunch')
            TimeSlot.objects.get_or_create(date_option=self, period='afternoon')


class TimeSlot(models.Model):
    PERIOD_CHOICES = [
        ('morning', _('Matin')),
        ('lunch', _('Repas')),
        ('afternoon', _('Après-midi')),
    ]
    
    date_option = models.ForeignKey(DateOption, on_delete=models.CASCADE, related_name='time_slots', verbose_name=_('Option de date'))
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, verbose_name=_('Période'))
    
    class Meta:
        verbose_name = _('Créneau horaire')
        verbose_name_plural = _('Créneaux horaires')
        unique_together = [['date_option', 'period']]
        ordering = ['date_option', 'period']
    
    def __str__(self):
        period_display = dict(self.PERIOD_CHOICES).get(self.period, self.period)
        return f"{self.date_option} - {period_display}"


class Vote(models.Model):
    CHOICE_CHOICES = [
        ('yes', _('Oui')),
        ('no', _('Non')),
        ('maybe', _('Peut-être')),
    ]

    time_slot = models.ForeignKey('TimeSlot', on_delete=models.CASCADE, related_name='votes', verbose_name=_('Créneau horaire'))
    child = models.ForeignKey('children.Child', on_delete=models.CASCADE, related_name='votes', verbose_name=_('Enfant'))
    choice = models.CharField(max_length=5, choices=CHOICE_CHOICES, verbose_name=_('Choix'))
    voted_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Date du vote'))
    
    class Meta:
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')
        unique_together = [['time_slot', 'child']]
        ordering = ['-voted_at']

    def __str__(self):
        child_name = str(self.child) if self.child else "Unknown"
        return f"{child_name} - {self.time_slot} - {self.choice}"
