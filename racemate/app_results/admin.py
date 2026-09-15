# app_results/admin.py
from django.contrib import admin
from .models import Participation, LapPlan, Lap

@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("start_entry", "is_participated", "age_group", "gender", "total_lap_time", "end_time", "certificate_generated")
    search_fields = ("start_entry__name", "start_entry__bib_id", "age_group", "gender")


@admin.register(LapPlan)
class LapPlanAdmin(admin.ModelAdmin):
    list_display = ("race", "gender", "laps_required")
    list_filter = ("race", "gender")


@admin.register(Lap)
class LapAdmin(admin.ModelAdmin):
    list_display = ("participation", "lap_number", "lap_time_mmss", "recorded_at")
    list_filter = ("lap_number",)
    search_fields = ("participation__start_entry__name", "participation__start_entry__bib_id")