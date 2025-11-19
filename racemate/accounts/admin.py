# accounts/admin.py
from django.contrib import admin
from .models import Registration
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str
import re

@admin.action(description="Export selected to CSV")
def export_to_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    # include concrete field names (legacy text 'district' is included here)
    field_names = [f.name for f in meta.fields]
    # include many-to-many names separately so we can join them
    m2m_names = [f.name for f in meta.many_to_many]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
    writer = csv.writer(response)

    # Write header: keep raw field names, but add a friendly column for district_fk name
    header = field_names + ['district_fk_name'] + m2m_names
    writer.writerow(header)

    for obj in queryset:
        row = []
        for field in field_names:
            value = getattr(obj, field)
            row.append(smart_str(value))
        # append district_fk name (friendly)
        fk_name = obj.district_fk.name if getattr(obj, 'district_fk', None) else ''
        row.append(smart_str(fk_name))
        # handle m2m fields by joining their string representations
        for m2m in m2m_names:
            related_qs = getattr(obj, m2m).all()
            names = [smart_str(x) for x in related_qs]
            row.append(", ".join(names))
        writer.writerow(row)
    return response

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'mobile_number',
        'get_district',          # shows FK name (fallback to legacy)
        'representing_from',
        'events_list',           # helper instead of raw M2M
        'created_at',
    )

    list_display_links = ('id', 'name')
    search_fields = (
        'name',
        'mobile_number',
        'aadhar_number',
        'district',              # legacy text
        'district_fk__name',     # FK name search
    )
    list_filter = ('profession', 'state', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25
    actions = [export_to_csv]

    def get_queryset(self, request):
        """
        Prefetch/select related to avoid N+1 queries when rendering list_display.
        """
        qs = super().get_queryset(request)
        # select_related for FK, prefetch for M2M
        return qs.select_related('district_fk', 'state').prefetch_related('events')

    def events_list(self, obj):
        """
        Safe, short representation of related events for the admin list view.
        Shows up to 4 names, with an ellipsis if more exist.
        """
        qs = obj.events.all()
        names = [e.name for e in qs]
        if not names:
            return ""
        if len(names) > 4:
            return ", ".join(names[:4]) + " …"
        return ", ".join(names)
    events_list.short_description = "Events"

    def get_district(self, obj):
        """
        Display the FK name if set, otherwise fall back to legacy text field.
        """
        if getattr(obj, 'district_fk', None):
            # return name attribute of FK
            return obj.district_fk.name
        # fallback to legacy free-text district
        return obj.district or "-"
    get_district.short_description = "District"
    get_district.admin_order_field = 'district_fk__name'

