# from django.contrib import admin
# from .models import dimState  # <-- import your model here

# # Register your models here.
# admin.site.register(dimState)



from django.contrib import admin
from .models import (
    DimState, DimDistrict, DimGender, DimEventType,
    DimEventCategory, dimDate
)

@admin.register(DimState)
class DimStateAdmin(admin.ModelAdmin):
    search_fields = ("name",)

# class DimDistrictAdmin(admin.ModelAdmin):
#     list_display = ("name", "state")
#     search_fields = ("name", "state__name")
#     list_filter = ("state",)

@admin.register(DimDistrict)
class DimDistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "state")   # show code in list
    list_editable = ("code",)                        # allow inline editing of code
    search_fields = ("name", "code", "state__name")  # enable searching by code too
    list_filter = ("state",)
    ordering = ("state__name", "name")
    list_per_page = 200

@admin.register(DimGender)
class DimGenderAdmin(admin.ModelAdmin):
    pass

@admin.register(DimEventType)
class DimEventTypeAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(DimEventCategory)
class DimEventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "event_type")
    list_filter = ("event_type",)

@admin.register(dimDate)
class dimDateAdmin(admin.ModelAdmin):
    list_display = ("date", "year", "quarter")
    search_fields = ("date",)

