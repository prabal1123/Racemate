# app_bib/views.py
from datetime import date, datetime
import re
import csv
from io import StringIO
from .forms import TimeEntryForm
from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django_filters.views import FilterView

from accounts.models import Registration
from django.contrib.auth.decorators import login_required 
from .filters import RegistrationFilter
from django.views.decorators.http import require_POST
from django.apps import apps
TimeEntry = apps.get_model('app_bib', 'TimeEntry')
from urllib.parse import parse_qs



@method_decorator(staff_member_required, name='dispatch')
class RegistrationBibListView(FilterView):
    model = Registration
    filterset_class = RegistrationFilter
    template_name = "app_bib/registration_bib_list.html"
    paginate_by = 25
    queryset = Registration.objects.select_related('district_fk', 'state').all()

    # map friendly sort keys to DB fields
    SORT_MAP = {
        'bib_id': 'bib_id',
        'district': 'district_fk__name',
        'gender': 'gender',
        # We use date_of_birth for age sorting (older DOB => older person).
        'age': 'date_of_birth',
    }
    DEFAULT_ORDERING = 'bib_id'

    def get_queryset(self):
        """
        Use FilterView's filterset to produce the filtered queryset, then apply ordering.
        """
        base_qs = self.queryset
        filterset = self.filterset_class(self.request.GET or None, queryset=base_qs)
        qs = filterset.qs

        sort = self.request.GET.get('sort')
        if sort:
            desc = sort.startswith('-')
            key = sort[1:] if desc else sort
            field = self.SORT_MAP.get(key)
            if field:
                order_field = f"-{field}" if desc else field
                qs = qs.order_by(order_field)
        else:
            qs = qs.order_by(self.DEFAULT_ORDERING)

        return qs

    def _compute_age_from_dob(self, dob, today=None):
        """Return integer age or None if dob is falsy."""
        if not dob:
            return None
        if today is None:
            today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age

    @staticmethod
    def _compute_short_bib(bib):
        """
        Remove the year segment from a full bib_id for public display.
        e.g. "MC-U23-M-2025-0001" -> "MC-U23-M-0001"
        Returns '—' for falsy values.
        """
        if not bib:
            return "—"
        parts = str(bib).split('-')
        # remove the first 4-digit segment (likely the year)
        for i, p in enumerate(parts):
            if re.fullmatch(r'\d{4}', p):
                parts.pop(i)
                return '-'.join(parts)
        # fallback: if a typical format with >=4 parts, remove index 3
        if len(parts) >= 4:
            parts.pop(3)
            return '-'.join(parts)
        return str(bib)

    def get(self, request, *args, **kwargs):
        """
        Add CSV export support. If ?export=csv is present, return CSV of the
        filtered & ordered queryset (unpaginated). Otherwise fall back to
        the normal FilterView GET handler (which renders the template).
        """
        if request.GET.get('export') == 'csv':
            return self._export_csv_response()
        return super().get(request, *args, **kwargs)

    def _export_csv_response(self):
        """
        Build and return an HttpResponse containing CSV for the current filter/sort.
        """
        qs = self.get_queryset()

        output = StringIO()
        output.write('\ufeff')  # BOM for Excel
        writer = csv.writer(output)

        writer.writerow([
            'bib_id',       # full canonical bib
            'bib_public',   # printable short bib (no year)
            'name',
            'district',
            'age',
            'gender',
            'bib_released_at',
        ])

        today = date.today()

        for reg in qs:
            bib_public = self._compute_short_bib(reg.bib_id)

            age_val = None
            age_on = getattr(reg, 'age_on', None)
            if callable(age_on):
                try:
                    age_val = age_on(today)
                except Exception:
                    age_val = None
            if age_val is None:
                dob = getattr(reg, 'date_of_birth', None)
                age_val = self._compute_age_from_dob(dob, today)

            district_name = None
            try:
                district_name = reg.district_fk.name
            except Exception:
                district_name = getattr(reg, 'district', None)

            gender_display = None
            try:
                gender_display = reg.get_gender_display()
            except Exception:
                gender_display = getattr(reg, 'gender', '')

            bib_released_at = reg.bib_released_at.isoformat() if getattr(reg, 'bib_released_at', None) else ''

            writer.writerow([
                reg.bib_id or '',
                bib_public,
                getattr(reg, 'name', '') or '',
                district_name or '',
                age_val if age_val is not None else '',
                gender_display or '',
                bib_released_at,
            ])

        filename = f"bib_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        params = self.request.GET.copy()
        if 'page' in params:
            params.pop('page')
        ctx['current_querystring'] = params.urlencode()
        ctx['current_sort'] = self.request.GET.get('sort', self.DEFAULT_ORDERING)

        today = date.today()
        page_obj = ctx.get('page_obj')
        if page_obj:
            for reg in page_obj.object_list:
                age_val = None
                age_on = getattr(reg, 'age_on', None)
                if callable(age_on):
                    try:
                        age_val = age_on(today)
                    except Exception:
                        age_val = None

                if age_val is None:
                    dob = getattr(reg, 'date_of_birth', None)
                    age_val = self._compute_age_from_dob(dob, today)

                reg.age_display = str(age_val) if age_val is not None else '—'
                reg.bib_public = self._compute_short_bib(reg.bib_id)

        return ctx

@login_required
def start_list_view(request):
    """
    Renders a start list table with:
      name, bib number, event, gender, age, start_time, end_time

    Robustness:
    - Only calls select_related for relation names that actually exist and are
      FK/OneToOne (avoids FieldError).
    - If event is ManyToMany, uses prefetch_related instead.
    - Computes `age_display` and `bib_public` for template convenience.
    - Sets `event_display` (string) on each reg instance so template can use
      {{ r.event_display }} regardless of the underlying model shape.
    """
    from django.db.models import ManyToManyField, ForeignKey, OneToOneField

    # Candidate relation/field names we might expect on Registration
    CANDIDATE_EVENT_FIELDS = (
        'event_fk', 'event', 'race', 'race_event', 'event_registration', 'event_name', 'race_name', 'events'
    )

    select_related_fields = []
    prefetch_related_fields = []
    plain_event_field = None

    # Inspect model fields and decide which related/prefetch fields to use.
    for name in CANDIDATE_EVENT_FIELDS:
        try:
            fld = Registration._meta.get_field(name)
            # If it's a FK/OneToOne -> use select_related
            if isinstance(fld, (ForeignKey, OneToOneField)):
                select_related_fields.append(name)
            # If it's M2M -> prefetch_related
            elif isinstance(fld, ManyToManyField):
                prefetch_related_fields.append(name)
            else:
                # it's some plain field (CharField, TextField, etc.)
                plain_event_field = name
        except Exception:
            # field not present — skip
            continue

    # Always include district/state if present (for display)
    for extra in ('district_fk', 'state'):
        try:
            fld = Registration._meta.get_field(extra)
            if isinstance(fld, (ForeignKey, OneToOneField)):
                if extra not in select_related_fields:
                    select_related_fields.append(extra)
        except Exception:
            pass

    # Build base queryset of registrations that have a bib assigned
    qs = Registration.objects.filter(bib_id__isnull=False)

    if select_related_fields:
        qs = qs.select_related(*select_related_fields)
    if prefetch_related_fields:
        qs = qs.prefetch_related(*prefetch_related_fields)

    # Evaluate queryset (we will annotate in-memory)
    registrations = list(qs)

    # Annotate useful display fields for the template
    today = date.today()
    for reg in registrations:
        # age_display (prefer model helper age_on if present)
        age_val = None
        age_on = getattr(reg, 'age_on', None)
        if callable(age_on):
            try:
                age_val = age_on(today)
            except Exception:
                age_val = None
        if age_val is None:
            dob = getattr(reg, 'date_of_birth', None)
            if dob:
                age_val = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        reg.age_display = str(age_val) if age_val is not None else '—'

        # public bib without year
        reg.bib_public = RegistrationBibListView._compute_short_bib(reg.bib_id)

        # Resolve event_display:
        event_obj = None
        # 1) If we have a select_related FK, try those first (skip district/state)
        for fname in select_related_fields:
            if fname in ('district_fk', 'state'):
                continue
            event_obj = getattr(reg, fname, None)
            if event_obj:
                break

        # 2) If not found, check prefetch m2m fields (use all related objects and join names)
        if event_obj is None and prefetch_related_fields:
            for fname in prefetch_related_fields:
                rel_qs = getattr(reg, fname, None)
                # rel_qs may be a manager/queryset; take all() if present
                try:
                    # gather names
                    names = [getattr(ev, 'name', None) or getattr(ev, 'title', None) or str(ev) for ev in rel_qs.all()]
                    if names:
                        event_obj = names  # store as list for joining later
                        break
                except Exception:
                    # maybe it's already evaluated list-like
                    try:
                        names = [getattr(ev, 'name', None) or getattr(ev, 'title', None) or str(ev) for ev in rel_qs]
                        if names:
                            event_obj = names
                            break
                    except Exception:
                        pass

        # 3) If event is stored as plain field on model (string)
        if event_obj is None and plain_event_field:
            event_val = getattr(reg, plain_event_field, None)
            reg.event_display = event_val or '—'
            continue

        # 4) If still None, try some common attribute names directly (fallback)
        if event_obj is None:
            for attr in ('event', 'race', 'event_name', 'race_name'):
                val = getattr(reg, attr, None)
                if val:
                    event_obj = val
                    break

        # Now convert event_obj (if present) to a display string
        if event_obj is None:
            reg.event_display = '—'
        else:
            # If event_obj is a list of names (from M2M), join them
            if isinstance(event_obj, (list, tuple)):
                reg.event_display = ', '.join(event_obj)
            else:
                reg.event_display = getattr(event_obj, 'name', None) or getattr(event_obj, 'title', None) or str(event_obj)

    context = {
        'registrations': registrations,
    }
    return render(request, 'app_bib/start_list.html', context)


@staff_member_required
@require_POST
def generate_bibs_view(request):
    """
    Generate bibs for the current filtered queryset.
    - Only staff can POST to this.
    - Accepts a hidden 'qs' POST field containing the current querystring so that
      filters applied on the list are honoured.
    """
    # Reconstruct filter data from POST 'qs' (querystring) if provided
    qs_string = request.POST.get('qs', '') or ''
    if qs_string:
        parsed = parse_qs(qs_string)
        # parse_qs gives lists for values; RegistrationFilter can accept that shape
        filter_data = parsed
    else:
        filter_data = {}

    # Build a base queryset (all registrations) and apply the same filterset used by the list view
    base_qs = Registration.objects.all()
    try:
        fs = RegistrationFilter(data=filter_data, queryset=base_qs)
        filtered_qs = fs.qs
    except Exception:
        filtered_qs = base_qs

    # Narrow to only those without bibs (null or empty)
    to_generate_qs = filtered_qs.filter(bib_id__isnull=True) | filtered_qs.filter(bib_id__exact='')
    regs = list(to_generate_qs)

    generated_count = 0
    errors = []
    for reg in regs:
        try:
            new_bib = reg.release_bib()
            # If your model method does not save, uncomment next line:
            # reg.save()
            if new_bib:
                generated_count += 1
        except Exception as exc:
            errors.append(f"{reg.pk}: {exc}")

    if generated_count:
        messages.success(request, f"Generated {generated_count} bib(s) for current results.")
    else:
        messages.info(request, "No registrations required bib generation (none matched or already have bibs).")

    if errors:
        messages.error(request, "Some items failed to generate; check server logs for details.")

    # Redirect back to list preserving querystring (if present)
    next_url = request.POST.get('next') or reverse('app_bib:registration_bib_list')
    if qs_string:
        redirect_to = f"{next_url}?{qs_string}"
    else:
        redirect_to = next_url
    return redirect(redirect_to)

def start_list_export_csv(request):
    """
    Export the start list as CSV:
    columns: name, bib number, event, gender, age, start_time, end_time
    """
    from io import StringIO
    import csv
    from datetime import date
    from django.db.models import ManyToManyField, ForeignKey, OneToOneField

    # Build queryset similarly (avoid N+1)
    select_related_fields = []
    prefetch_related_fields = []

    for extra in ('district_fk', 'state'):
        try:
            fld = Registration._meta.get_field(extra)
            if isinstance(fld, (ForeignKey, OneToOneField)):
                select_related_fields.append(extra)
        except Exception:
            pass

    try:
        fld_events = Registration._meta.get_field('events')
        if isinstance(fld_events, ManyToManyField):
            prefetch_related_fields.append('events')
        elif isinstance(fld_events, (ForeignKey, OneToOneField)):
            select_related_fields.append('events')
    except Exception:
        pass

    qs = Registration.objects.filter(bib_id__isnull=False)
    if select_related_fields:
        qs = qs.select_related(*select_related_fields)
    if prefetch_related_fields:
        qs = qs.prefetch_related(*prefetch_related_fields)

    # Prepare CSV
    output = StringIO()
    output.write('\ufeff')  # BOM for Excel/Excel-like apps
    writer = csv.writer(output)

    writer.writerow(['name', 'bib_number', 'event', 'gender', 'age', 'start_time', 'end_time'])

    today = date.today()
    for reg in qs:
        # name
        name = getattr(reg, 'name', '') or ''

        # bib_public if computed on object, else compute here
        bib_public = getattr(reg, 'bib_public', None)
        if not bib_public:
            try:
                bib_public = RegistrationBibListView._compute_short_bib(reg.bib_id)
            except Exception:
                bib = getattr(reg, 'bib_id', '')
                if not bib:
                    bib_public = ''
                else:
                    parts = str(bib).split('-')
                    for i, p in enumerate(parts):
                        if re.fullmatch(r'\d{4}', p):
                            parts.pop(i)
                            bib_public = '-'.join(parts)
                            break
                    else:
                        bib_public = str(bib)

        # event_display resolution (reuse same logic)
        event_display = ''
        events_rel = getattr(reg, 'events', None)
        if events_rel is not None:
            try:
                names = [getattr(ev, 'name', None) or getattr(ev, 'title', None) or str(ev) for ev in events_rel.all()]
                if names:
                    event_display = ', '.join(names)
            except Exception:
                try:
                    names = [getattr(ev, 'name', None) or getattr(ev, 'title', None) or str(ev) for ev in events_rel]
                    if names:
                        event_display = ', '.join(names)
                except Exception:
                    event_display = ''

        if not event_display:
            for attr in ('event_fk', 'event', 'event_name', 'race', 'race_event'):
                try:
                    val = getattr(reg, attr, None)
                except Exception:
                    val = None
                if val:
                    event_display = getattr(val, 'name', None) or getattr(val, 'title', None) or str(val)
                    break

        # gender
        try:
            gender_display = reg.get_gender_display()
        except Exception:
            gender_display = getattr(reg, 'gender', '') or ''

        # age
        age_val = ''
        age_on = getattr(reg, 'age_on', None)
        if callable(age_on):
            try:
                age_val = age_on(today)
            except Exception:
                age_val = ''
        if age_val in (None, ''):
            dob = getattr(reg, 'date_of_birth', None)
            if dob:
                age_val = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        start_time = getattr(reg, 'start_time', '') or ''
        end_time = getattr(reg, 'end_time', '') or ''

        writer.writerow([name, bib_public, event_display, gender_display, age_val, start_time, end_time])

    filename = f"start_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

@login_required
def time_entry_list_create(request):
    if request.method == 'POST':
        form = TimeEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Time entry saved.")
            return redirect(reverse('app_bib:time_entry'))
        else:
            messages.error(request, "Please fix errors below.")
    else:
        form = TimeEntryForm()

    entries = TimeEntry.objects.all()[:200]  # limit; adjust as needed
    context = {
        'form': form,
        'entries': entries,
    }
    return render(request, 'app_bib/time_entry.html', context)