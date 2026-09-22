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
    
    # Restrictions
    restrict_children_under_6 = models.BooleanField(default=False, verbose_name=_('Limiter enfants < 6 ans'))
    max_children_under_6 = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Max enfants < 6 ans'))
    restrict_children_over_6 = models.BooleanField(default=False, verbose_name=_('Limiter enfants >= 6 ans'))
    max_children_over_6 = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Max enfants >= 6 ans'))
    restrict_total_children = models.BooleanField(default=False, verbose_name=_('Limiter total enfants'))
    max_total_children = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Max total enfants'))
    restrict_days_under_6 = models.BooleanField(default=False, verbose_name=_('Limiter nombre de jours réservés par enfant < 6 ans'))
    max_days_under_6 = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Max nombre de jours réservés par enfant < 6 ans'))
    restrict_days_over_6 = models.BooleanField(default=False, verbose_name=_('Limiter nombre de jours réservés par enfant >= 6 ans'))
    max_days_over_6 = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('Max nombre de jours réservés par enfant >= 6 ans'))
    
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
                yes_under_six = sum(vote.child.age() < 6 for vote in yes_votes)
                total = yes_count + no_count + maybe_count
                
                stats.append({
                    'option': option,
                    'time_slot': time_slot,
                    'yes': yes_count,
                    'yes_under_six': yes_under_six,
                    'yes_over_six': yes_count - yes_under_six,
                    'no': no_count,
                    'maybe': maybe_count,
                    'total': total,
                    'yes_percent': (yes_count / total * 100) if total > 0 else 0,
                    'no_percent': (no_count / total * 100) if total > 0 else 0,
                    'maybe_percent': (maybe_count / total * 100) if total > 0 else 0,
                    'yes_children': [str(vote.child) for vote in yes_votes.order_by('child__last_name', 'child__first_name')],
                    'no_children': [str(vote.child) for vote in no_votes.order_by('child__last_name', 'child__first_name')],
                    'maybe_children': [str(vote.child) for vote in maybe_votes.order_by('child__last_name', 'child__first_name')],
                    # Expose vote objects for admin interactions
                    'yes_votes': yes_votes.order_by('child__last_name', 'child__first_name'),
                    'no_votes': no_votes.order_by('child__last_name', 'child__first_name'),
                })
        return stats

    def get_yes_days_by_child(self, child):
        """Get count of days with at least one 'yes' for a given child"""
        options = []
        for option in self.date_options.all():
            option_yes = False
            for time_slot in option.time_slots.all():
                if time_slot.votes.filter(child=child, choice='yes').exists():
                    option_yes = True
                    break
            if option_yes:
                options.append(option)
        return options

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
    
    def get_yes_votes_by_age_group(self):
        """Get count of 'yes' votes grouped by age (under 6, over 6)"""
        yes_votes = self.votes.filter(choice='yes').select_related('child')
        under_six = sum(1 for vote in yes_votes if vote.child.age() < 6)
        over_six = sum(1 for vote in yes_votes if vote.child.age() >= 6)
        return {
            'under_6': under_six,
            'over_6': over_six,
            'total': under_six + over_six
        }
    
    def check_restrictions(self, child_to_add=None):
        """
        Check if restrictions are met for 'yes' votes.
        Returns: {'valid': bool, 'errors': [list of error messages]}
        If child_to_add is provided, checks if adding this child would violate restrictions.
        """
        date_group = self.date_option.date_group
        errors = []
        
        counts = self.get_yes_votes_by_age_group()
        
        # Check if we need to account for a child to be added
        if child_to_add:
            if child_to_add.age() < 6:
                counts['under_6'] += 1
            else:
                counts['over_6'] += 1
            counts['total'] += 1
        
        # Check children under 6 restriction
        if date_group.restrict_children_under_6 and date_group.max_children_under_6:
            if counts['under_6'] > date_group.max_children_under_6:
                errors.append(_('Limite d\'enfants de moins de 6 ans dépassée (max: %(max)d)') % {'max': date_group.max_children_under_6})
        
        # Check children over 6 restriction
        if date_group.restrict_children_over_6 and date_group.max_children_over_6:
            if counts['over_6'] > date_group.max_children_over_6:
                errors.append(_('Limite d\'enfants de 6 ans ou plus dépassée (max: %(max)d)') % {'max': date_group.max_children_over_6})
        
        # Check total children restriction
        if date_group.restrict_total_children and date_group.max_total_children:
            if counts['total'] > date_group.max_total_children:
                errors.append(_('Limite du nombre total d\'enfants dépassée (max: %(max)d)') % {'max': date_group.max_total_children})

        if child_to_add:
            # Check if adding this child would exceed the max days for their age group
            max_days = 0
            if child_to_add.age() < 6 and date_group.restrict_days_under_6 and date_group.max_days_under_6:
                max_days = date_group.max_days_under_6
            elif child_to_add.age() >= 6 and date_group.restrict_days_over_6 and date_group.max_days_over_6:
                max_days = date_group.max_days_over_6

            if max_days > 0:
                if self.date_option in date_group.get_yes_days_by_child(child_to_add):
                    # Child already has a 'yes' for this date option, so no new day is added
                    pass
                else:
                    if len(date_group.get_yes_days_by_child(child_to_add)) + 1 > max_days:
                        errors.append(_('Limite du nombre de jours réservés dépassée pour %(child)s (max: %(max)d)') % {'child': str(child_to_add), 'max': max_days})
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'counts': counts
        }


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
