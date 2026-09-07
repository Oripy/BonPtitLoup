from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .forms import RegistrationForm, LoginForm, PasswordChangeForm
from .models import CustomUser


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, _('Compte créé pour %(username)s ! Veuillez vous connecter.') % {'username': username})
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('identifier')
            password = form.cleaned_data.get('password')
            account = CustomUser.objects.filter(username=identifier).first()
            if account is None:
                account = CustomUser.objects.filter(email__iexact=identifier).first()
            user = authenticate(
                request,
                username=account.username if account else None,
                password=password,
            )
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, _('Nom d\'utilisateur ou mot de passe invalide.'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, _('Vous avez été déconnecté avec succès.'))
    return redirect('accounts:login')


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, _('Votre mot de passe a été modifié avec succès.'))
            return redirect('accounts:change_password')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
