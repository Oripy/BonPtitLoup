from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    """Home view that redirects based on user role"""
    # Superusers and staff are treated as admins
    if request.user.is_admin or request.user.is_superuser or request.user.is_staff:
        return redirect('admin_panel:dashboard')
    elif request.user.is_parent:
        return redirect('children:dashboard')
    else:
        # If user has no role, redirect to login (they shouldn't be able to login without a role)
        return redirect('accounts:login')

