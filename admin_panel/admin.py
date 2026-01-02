from django.contrib import admin
from .models import WelcomePage


@admin.register(WelcomePage)
class WelcomePageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'updated_at', 'updated_by']
    readonly_fields = ['updated_at', 'updated_by']
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
