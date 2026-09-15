
from django.contrib import admin
from .models import Race, Event, RaceRegistration

# --- INLINE FOR EVENTS ---
class EventInline(admin.TabularInline):
    model = Event
    extra = 2  # Shows two empty rows to add "Mass Start", "Time Trial" quickly
    fields = ('title', 'distance_km', 'price')

# --- ADMIN CLASSES ---

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'race_start', 'get_rider_count', 'status')
    search_fields = ('name', 'location')
    list_filter = ('race_start',)
    # This allows you to add events directly inside the Race page
    inlines = [EventInline]

    def get_rider_count(self, obj):
        # Updated to the new related_name we set in the model
        return obj.race_registrations.count()
    get_rider_count.short_description = 'Total Registered Riders'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'race', 'distance_km', 'price')
    list_filter = ('race',)
    search_fields = ('title', 'race__name')

# @admin.register(DoublesEntry)
# class DoublesEntryAdmin(admin.ModelAdmin):
#     list_display = (
#         'event',
#         'player_one',
#         'player_two',
#         'created_at',
#     )

#     list_filter = (
#         'event__race',
#         'event',
#         'created_at',
#     )

#     search_fields = (
#         'player_one__name',
#         'player_two__name',
#         'event__title',
#         'event__race__name',
#     )

#     autocomplete_fields = (
#         'event',
#         'player_one',
#         'player_two',
#     )

@admin.register(RaceRegistration)
class RaceRegistrationAdmin(admin.ModelAdmin):
    # Added 'event' to the list display so you can see exactly what they joined
    list_display = ('participant', 'event', 'race', 'created_at')
    list_filter = ('race', 'event', 'created_at')
    search_fields = ('participant__name', 'race__name', 'event__title')