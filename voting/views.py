from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.db.models import Q
from children.models import Child
from .models import DateGroup, DateOption, TimeSlot, Vote


@login_required
def date_group_list(request):
    """List all active and closed date groups"""
    date_groups = DateGroup.objects.filter(
        Q(status='active') | Q(status='closed')
    ).prefetch_related('date_options__time_slots')
    children = Child.objects.filter(parent=request.user)
    
    # Get votes for each child for each group
    user_votes_dict = {}
    for group in date_groups:
        group_votes = {}
        for child in children:
            votes = Vote.objects.filter(
                child=child,
                time_slot__date_option__date_group=group
            ).select_related('time_slot', 'time_slot__date_option')
            group_votes[child.id] = {vote.time_slot.id: vote.choice for vote in votes}
        user_votes_dict[group.id] = group_votes
    
    context = {
        'date_groups': date_groups,
        'user_votes_dict': user_votes_dict,
        'children': children,
    }
    return render(request, 'voting/date_group_list.html', context)


@login_required
def vote_view(request, group_id):
    """Vote on a date group for each child and each time slot"""
    date_group = get_object_or_404(DateGroup, pk=group_id)
    
    # Check if voting is allowed
    if not date_group.can_vote():
        messages.warning(request, _('Ce groupe de dates est fermé. Vous ne pouvez plus voter, mais vous pouvez consulter les résultats.'))
        return redirect('voting:results', group_id=group_id)
    
    date_options = date_group.date_options.prefetch_related('time_slots')
    children = Child.objects.filter(parent=request.user)
    
    if not children.exists():
        messages.warning(request, _('Vous devez enregistrer au moins un enfant avant de voter.'))
        return redirect('children:dashboard')
    
    if request.method == 'POST':
        # Process votes for each child and each time slot
        votes_created = 0
        votes_updated = 0
        votes_deleted = 0
        
        for child in children:
            for option in date_options:
                for time_slot in option.time_slots.all():
                    choice_key = f'choice_{child.id}_{time_slot.id}'
                    choice = request.POST.get(choice_key, '')
                    
                    if choice in ['yes', 'no', 'maybe']:
                        vote, created = Vote.objects.update_or_create(
                            time_slot=time_slot,
                            child=child,
                            defaults={'choice': choice}
                        )
                        if created:
                            votes_created += 1
                        else:
                            votes_updated += 1
                    elif choice == '':
                        # Clear vote if empty value is selected
                        deleted = Vote.objects.filter(
                            time_slot=time_slot,
                            child=child
                        ).delete()[0]
                        if deleted > 0:
                            votes_deleted += 1
        
        if votes_created > 0 or votes_updated > 0:
            messages.success(request, _('Vos votes ont été enregistrés avec succès !'))
        elif votes_deleted > 0:
            messages.success(request, _('Vos votes ont été effacés avec succès !'))
        else:
            messages.info(request, _('Aucune modification n\'a été apportée.'))
        
        return redirect('voting:list')
    
    # Get existing votes per child
    existing_votes = {}
    for child in children:
        child_votes = {}
        votes = Vote.objects.filter(
            child=child,
            time_slot__date_option__date_group=date_group
        ).select_related('time_slot', 'time_slot__date_option')
        for vote in votes:
            child_votes[vote.time_slot.id] = vote.choice
        existing_votes[child.id] = child_votes
    
    context = {
        'date_group': date_group,
        'date_options': date_options,
        'children': children,
        'existing_votes': existing_votes,
    }
    return render(request, 'voting/vote.html', context)


@login_required
def results_view(request, group_id):
    """View voting results for a date group"""
    date_group = get_object_or_404(DateGroup, pk=group_id)
    statistics = date_group.get_vote_statistics()
    
    context = {
        'date_group': date_group,
        'statistics': statistics,
    }
    return render(request, 'voting/results.html', context)
