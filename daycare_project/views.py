from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """Home view that redirects based on user role"""
    if request.user.is_admin:
        return redirect('admin_panel:dashboard')
    elif request.user.is_parent:
        return redirect('children:dashboard')
    else:
        return redirect('accounts:login')

