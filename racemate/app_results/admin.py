# app_results/admin.py
from django.contrib import admin
from .models import Participation

@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("start_entry", "is_participated", "age_group", "gender", "total_lap_time", "end_time", "certificate_generated")
    search_fields = ("start_entry__name", "start_entry__bib_id", "age_group", "gender")
