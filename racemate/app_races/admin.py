# from django.contrib import admin
# from .models import Race, RaceRegistration
# from .models import Race, Heat

# @admin.register(Race)
# class RaceAdmin(admin.ModelAdmin):
#     # This shows these columns in the admin list view
#     list_display = ('name', 'location', 'race_start', 'get_rider_count', 'status')

#     def get_rider_count(self, obj):
#         return obj.registrations.count()
#     get_rider_count.short_description = 'Registered Riders'

# admin.site.register(RaceRegistration)

# @admin.register(Heat)
# class HeatAdmin(admin.ModelAdmin):
#     list_display = ('name', 'race', 'actual_start_time')
#     list_filter = ('race',)


# from django.contrib import admin
# from .models import Race, RaceRegistration

# # --- ADMIN CLASSES ---

# @admin.register(Race)
# class RaceAdmin(admin.ModelAdmin):
#     list_display = ('name', 'location', 'race_start', 'get_rider_count', 'status')
#     search_fields = ('name', 'location')
#     list_filter = ('race_start',)
#     # REMOVED: inlines = [HeatInline] (Heats are now just numbers on the athletes)

#     def get_rider_count(self, obj):
#         return obj.race_registrations.count()
#     get_rider_count.short_description = 'Registered Riders'


# # REMOVED: @admin.register(Heat) class HeatAdmin (This model no longer exists)


# @admin.register(RaceRegistration)
# class RaceRegistrationAdmin(admin.ModelAdmin):
#     list_display = ('participant', 'race', 'created_at')
#     list_filter = ('race', 'created_at')
#     # search_fields uses double underscore to look into the linked Registration model
#     search_fields = ('participant__name', 'race__name')

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


@admin.register(RaceRegistration)
class RaceRegistrationAdmin(admin.ModelAdmin):
    # Added 'event' to the list display so you can see exactly what they joined
    list_display = ('participant', 'event', 'race', 'created_at')
    list_filter = ('race', 'event', 'created_at')
    search_fields = ('participant__name', 'race__name', 'event__title')