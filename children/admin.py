from django.contrib import admin
from .models import Child


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'age', 'parent')
    list_filter = ('parent', 'birth_date')
    search_fields = ('first_name', 'last_name', 'parent__username', 'parent__email')
    readonly_fields = ('age',)
