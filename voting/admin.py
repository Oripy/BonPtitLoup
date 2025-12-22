from django.contrib import admin
from .models import DateGroup, DateOption, TimeSlot, Vote


class DateOptionInline(admin.TabularInline):
    model = DateOption
    extra = 1


@admin.register(DateGroup)
class DateGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active', 'status', 'get_total_votes')
    list_filter = ('is_active', 'status', 'created_at')
    search_fields = ('title', 'description')
    inlines = [DateOptionInline]
    readonly_fields = ('created_at',)

    def get_total_votes(self, obj):
        return obj.get_total_votes()
    get_total_votes.short_description = 'Total Votes'


class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
    extra = 0
    can_delete = False
    readonly_fields = ('period',)


@admin.register(DateOption)
class DateOptionAdmin(admin.ModelAdmin):
    list_display = ('date_group', 'date')
    list_filter = ('date_group', 'date')
    search_fields = ('date_group__title',)
    inlines = [TimeSlotInline]


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('date_option', 'period', 'get_vote_count')
    list_filter = ('period', 'date_option__date_group')
    search_fields = ('date_option__date_group__title',)
    
    def get_vote_count(self, obj):
        return obj.votes.count()
    get_vote_count.short_description = 'Nombre de votes'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('child', 'child__parent', 'time_slot', 'choice', 'voted_at')
    list_filter = ('choice', 'voted_at', 'time_slot__date_option__date_group', 'time_slot__period')
    search_fields = ('child__name', 'child__parent__username', 'time_slot__date_option__date_group__title')
    
    def child__parent(self, obj):
        return obj.child.parent.username
    child__parent.short_description = 'Parent'
