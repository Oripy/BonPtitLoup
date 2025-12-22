from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Child
from .forms import ChildForm


@login_required
def dashboard(request):
    """Parent dashboard showing all their children"""
    children = Child.objects.filter(parent=request.user)
    return render(request, 'children/dashboard.html', {'children': children})


@login_required
def child_create(request):
    """Create a new child"""
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user
            child.save()
            messages.success(request, _('%(name)s a été ajouté avec succès !') % {'name': child.name})
            return redirect('children:dashboard')
    else:
        form = ChildForm()
    return render(request, 'children/child_form.html', {'form': form, 'title': _('Ajouter un enfant')})


@login_required
def child_edit(request, pk):
    """Edit an existing child"""
    child = get_object_or_404(Child, pk=pk, parent=request.user)
    if request.method == 'POST':
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            messages.success(request, _('%(name)s a été mis à jour avec succès !') % {'name': child.name})
            return redirect('children:dashboard')
    else:
        form = ChildForm(instance=child)
    return render(request, 'children/child_form.html', {'form': form, 'title': _('Modifier un enfant'), 'child': child})


@login_required
def child_delete(request, pk):
    """Delete a child"""
    child = get_object_or_404(Child, pk=pk, parent=request.user)
    if request.method == 'POST':
        child_name = child.name
        child.delete()
        messages.success(request, _('%(name)s a été supprimé avec succès !') % {'name': child_name})
        return redirect('children:dashboard')
    return render(request, 'children/child_confirm_delete.html', {'child': child})
