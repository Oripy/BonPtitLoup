from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Prefetch
from django.utils.translation import gettext as _
import csv
from accounts.models import CustomUser
from children.models import Child
from voting.models import DateGroup, DateOption, TimeSlot, Vote
from .forms import DateGroupForm, DateOptionFormSet


def is_admin(user):
    """Check if user is an admin"""
    return user.is_authenticated and user.is_admin


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard"""
    date_groups = DateGroup.objects.all().annotate(
        total_votes=Count('date_options__time_slots__votes')
    ).order_by('-created_at')
    
    context = {
        'date_groups': date_groups,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def date_group_create(request):
    """Create a new date group"""
    if request.method == 'POST':
        form = DateGroupForm(request.POST)
        formset = DateOptionFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            date_group = form.save(commit=False)
            date_group.created_by = request.user
            date_group.save()
            formset.instance = date_group
            formset.save()
            messages.success(request, _('Le groupe de dates "%(title)s" a été créé avec succès !') % {'title': date_group.title})
            return redirect('admin_panel:dashboard')
    else:
        form = DateGroupForm()
        formset = DateOptionFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': _('Créer un groupe de dates'),
    }
    return render(request, 'admin_panel/date_group_form.html', context)


@login_required
@user_passes_test(is_admin)
def date_group_edit(request, pk):
    """Edit an existing date group"""
    date_group = get_object_or_404(DateGroup, pk=pk)
    
    if request.method == 'POST':
        form = DateGroupForm(request.POST, instance=date_group)
        formset = DateOptionFormSet(request.POST, instance=date_group)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, _('Le groupe de dates "%(title)s" a été mis à jour avec succès !') % {'title': date_group.title})
            return redirect('admin_panel:dashboard')
    else:
        form = DateGroupForm(instance=date_group)
        formset = DateOptionFormSet(instance=date_group)
    
    context = {
        'form': form,
        'formset': formset,
        'title': _('Modifier un groupe de dates'),
        'date_group': date_group,
    }
    return render(request, 'admin_panel/date_group_form.html', context)


@login_required
@user_passes_test(is_admin)
def date_group_delete(request, pk):
    """Delete a date group"""
    date_group = get_object_or_404(DateGroup, pk=pk)
    
    if request.method == 'POST':
        title = date_group.title
        date_group.delete()
        messages.success(request, _('Le groupe de dates "%(title)s" a été supprimé avec succès !') % {'title': title})
        return redirect('admin_panel:dashboard')
    
    context = {
        'date_group': date_group,
    }
    return render(request, 'admin_panel/date_group_confirm_delete.html', context)


@login_required
@user_passes_test(is_admin)
def results_view(request, pk):
    """View detailed voting results for a date group"""
    date_group = get_object_or_404(DateGroup, pk=pk)
    statistics = date_group.get_vote_statistics()
    
    context = {
        'date_group': date_group,
        'statistics': statistics,
    }
    return render(request, 'admin_panel/results.html', context)


@login_required
@user_passes_test(is_admin)
def export_csv(request, pk):
    """Export voting results to CSV"""
    date_group = get_object_or_404(DateGroup, pk=pk)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{date_group.title}_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Période', 'Oui', 'Non', 'Peut-être', 'Total Votes', 'Oui %', 'Non %', 'Peut-être %'])
    
    statistics = date_group.get_vote_statistics()
    for stat in statistics:
        writer.writerow([
            str(stat['option'].date),
            stat['time_slot'].get_period_display(),
            stat['yes'],
            stat['no'],
            stat['maybe'],
            stat['total'],
            f"{stat['yes_percent']:.1f}%",
            f"{stat['no_percent']:.1f}%",
            f"{stat['maybe_percent']:.1f}%",
        ])
    
    return response


@login_required
@user_passes_test(is_admin)
def export_excel(request, pk):
    """Export voting results to Excel"""
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
        
        date_group = get_object_or_404(DateGroup, pk=pk)
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Voting Results"
        
        # Header
        headers = ['Date', 'Période', 'Oui', 'Non', 'Peut-être', 'Total Votes', 'Oui %', 'Non %', 'Peut-être %']
        ws.append(headers)
        
        # Style header
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Data
        statistics = date_group.get_vote_statistics()
        for stat in statistics:
            ws.append([
                str(stat['option'].date),
                stat['time_slot'].get_period_display(),
                stat['yes'],
                stat['no'],
                stat['maybe'],
                stat['total'],
                f"{stat['yes_percent']:.1f}%",
                f"{stat['no_percent']:.1f}%",
                f"{stat['maybe_percent']:.1f}%",
            ])
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{date_group.title}_results.xlsx"'
        wb.save(response)
        return response
    except ImportError:
        messages.error(request, _('L\'export Excel nécessite openpyxl. Veuillez l\'installer.'))
        return redirect('admin_panel:results', pk=pk)


@login_required
@user_passes_test(is_admin)
def parents_list(request):
    """List all registered parents with their email and children"""
    parents = CustomUser.objects.filter(is_parent=True).prefetch_related(
        Prefetch('children', queryset=Child.objects.order_by('name'))
    ).order_by('last_name', 'first_name')
    
    context = {
        'parents': parents,
    }
    return render(request, 'admin_panel/parents_list.html', context)


@login_required
@user_passes_test(is_admin)
def reset_parent_password(request, parent_id):
    """Reset a parent's password to 0000"""
    parent = get_object_or_404(CustomUser, pk=parent_id, is_parent=True)
    
    if request.method == 'POST':
        parent.set_password('0000')
        parent.save()
        messages.success(request, _('Le mot de passe de %(name)s a été réinitialisé à 0000.') % {'name': f"{parent.first_name} {parent.last_name}"})
        return redirect('admin_panel:parents_list')
    
    context = {
        'parent': parent,
    }
    return render(request, 'admin_panel/reset_password_confirm.html', context)
