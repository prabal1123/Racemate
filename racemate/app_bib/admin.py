# from django.contrib import admin
# from .models import TimeEntry

# @admin.register(TimeEntry)
# class TimeEntryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'bib_id', 'lap_time', 'note', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('bib_id', 'note')
#     ordering = ('-created_at',)

from django.contrib import admin
from django.apps import apps

TimeEntry = apps.get_model('app_bib', 'TimeEntry')

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'bib_id', 'lap_time', 'note', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('bib_id', 'note')
    ordering = ('-created_at',)
