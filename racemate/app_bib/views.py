# # app_bib/views.py
# from datetime import date, datetime
# import re
# import csv
# from io import StringIO
# from .forms import TimeEntryForm
# from django.shortcuts import redirect
# from django.urls import reverse
# from django.shortcuts import render
# from django.contrib import messages
# from django.http import HttpResponse
# from django.utils import timezone
# from django.utils.decorators import method_decorator
# from django.contrib.admin.views.decorators import staff_member_required
# from django_filters.views import FilterView

# from accounts.models import Registration
# from django.contrib.auth.decorators import login_required 
# from .filters import RegistrationFilter
# from django.views.decorators.http import require_POST
# from django.apps import apps
# TimeEntry = apps.get_model('app_bib', 'TimeEntry')
# from urllib.parse import parse_qs



# @method_decorator(staff_member_required, name='dispatch')
# class RegistrationBibListView(FilterView):
#     model = Registration
#     filterset_class = RegistrationFilter
#     template_name = "app_bib/registration_bib_list.html"
#     paginate_by = 25
#     queryset = Registration.objects.select_related('district_fk', 'state').all()

#     # map friendly sort keys to DB fields
#     SORT_MAP = {
#         'bib_id': 'bib_id',
#         'district': 'district_fk__name',
#         'gender': 'gender',
#         # We use date_of_birth for age sorting (older DOB => older person).
#         'age': 'date_of_birth',
#     }
#     DEFAULT_ORDERING = 'bib_id'

#     def get_queryset(self):
#         """
#         Use FilterView's filterset to produce the filtered queryset, then apply ordering.
#         """
#         base_qs = self.queryset
#         filterset = self.filterset_class(self.request.GET or None, queryset=base_qs)
#         qs = filterset.qs

#         sort = self.request.GET.get('sort')
#         if sort:
#             desc = sort.startswith('-')
#             key = sort[1:] if desc else sort
#             field = self.SORT_MAP.get(key)
#             if field:
#                 order_field = f"-{field}" if desc else field
#                 qs = qs.order_by(order_field)
#         else:
#             qs = qs.order_by(self.DEFAULT_ORDERING)

#         return qs

#     def _compute_age_from_dob(self, dob, today=None):
#         """Return integer age or None if dob is falsy."""
#         if not dob:
#             return None
#         if today is None:
#             today = date.today()
#         age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
#         return age

#     @staticmethod
#     def _compute_short_bib(bib):
#         """
#         Remove the year segment from a full bib_id for public display.
#         e.g. "MC-U23-M-2025-0001" -> "MC-U23-M-0001"
#         Returns '—' for falsy values.
#         """
#         if not bib:
#             return "—"
#         parts = str(bib).split('-')
#         # remove the first 4-digit segment (likely the year)
#         for i, p in enumerate(parts):
#             if re.fullmatch(r'\d{4}', p):
#                 parts.pop(i)
#                 return '-'.join(parts)
#         # fallback: if a typical format with >=4 parts, remove index 3
#         if len(parts) >= 4:
#             parts.pop(3)
#             return '-'.join(parts)
#         return str(bib)

#     def get(self, request, *args, **kwargs):
#         """
#         Add CSV export support. If ?export=csv is present, return CSV of the
#         filtered & ordered queryset (unpaginated). Otherwise fall back to
#         the normal FilterView GET handler (which renders the template).
#         """
#         if request.GET.get('export') == 'csv':
#             return self._export_csv_response()
#         return super().get(request, *args, **kwargs)

#     def _export_csv_response(self):
#         """
#         Build and return an HttpResponse containing CSV for the current filter/sort.
#         """
#         qs = self.get_queryset()

#         output = StringIO()
#         output.write('\ufeff')  # BOM for Excel
#         writer = csv.writer(output)

#         writer.writerow([
#             'bib_id',       # full canonical bib
#             'bib_public',   # printable short bib (no year)
#             'name',
#             'district',
#             'age',
#             'gender',
#             'bib_released_at',
#         ])

#         today = date.today()

#         for reg in qs:
#             bib_public = self._compute_short_bib(reg.bib_id)

#             age_val = None
#             age_on = getattr(reg, 'age_on', None)
#             if callable(age_on):
#                 try:
#                     age_val = age_on(today)
#                 except Exception:
#                     age_val = None
#             if age_val is None:
#                 dob = getattr(reg, 'date_of_birth', None)
#                 age_val = self._compute_age_from_dob(dob, today)

#             district_name = None
#             try:
#                 district_name = reg.district_fk.name
#             except Exception:
#                 district_name = getattr(reg, 'district', None)

#             gender_display = None
#             try:
#                 gender_display = reg.get_gender_display()
#             except Exception:
#                 gender_display = getattr(reg, 'gender', '')

#             bib_released_at = reg.bib_released_at.isoformat() if getattr(reg, 'bib_released_at', None) else ''

#             writer.writerow([
#                 reg.bib_id or '',
#                 bib_public,
#                 getattr(reg, 'name', '') or '',
#                 district_name or '',
#                 age_val if age_val is not None else '',
#                 gender_display or '',
#                 bib_released_at,
#             ])

#         filename = f"bib_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#         response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         return response

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)

#         params = self.request.GET.copy()
#         if 'page' in params:
#             params.pop('page')
#         ctx['current_querystring'] = params.urlencode()
#         ctx['current_sort'] = self.request.GET.get('sort', self.DEFAULT_ORDERING)

#         today = date.today()
#         page_obj = ctx.get('page_obj')
#         if page_obj:
#             for reg in page_obj.object_list:
#                 age_val = None
#                 age_on = getattr(reg, 'age_on', None)
#                 if callable(age_on):
#                     try:
#                         age_val = age_on(today)
#                     except Exception:
#                         age_val = None

#                 if age_val is None:
#                     dob = getattr(reg, 'date_of_birth', None)
#                     age_val = self._compute_age_from_dob(dob, today)

#                 reg.age_display = str(age_val) if age_val is not None else '—'
#                 reg.bib_public = self._compute_short_bib(reg.bib_id)

#         return ctx

# @login_required
# def start_list_view(request):
#     """
#     Renders a start list table with:
#       name, bib number, event, gender, age, start_time, end_time

#     Robustness:
#     - Only calls select_related for relation names that actually exist and are
#       FK/OneToOne (avoids FieldError).
#     - If event is ManyToMany, uses prefetch_related instead.
#     - Computes `age_display` and `bib_public` for template convenience.
#     - Sets `event_display` (string) on each reg instance so template can use
#       {{ r.event_display }} regardless of the underlying model shape.
#     """
#     from django.db.models import ManyToManyField, ForeignKey, OneToOneField

#     # Candidate relation/field names we might expect on Registration
#     CANDIDATE_EVENT_FIELDS = (
#         'event_fk', 'event', 'race', 'race_event', 'event_registration', 'event_name', 'race_name', 'events'
#     )

#     select_related_fields = []
#     prefetch_related_fields = []
#     plain_event_field = None

#     # Inspect model fields and decide which related/prefetch fields to use.
#     for name in CANDIDATE_EVENT_FIELDS:
#         try:
#             fld = Registration._meta.get_field(name)
#             # If it's a FK/OneToOne -> use select_related
#             if isinstance(fld, (ForeignKey, OneToOneField)):
#                 select_related_fields.append(name)
#             # If it's M2M -> prefetch_related
#             elif isinstance(fld, ManyToManyField):
#                 prefetch_related_fields.append(name)
#             else:
#                 # it's some plain field (CharField, TextField, etc.)
#                 plain_event_field = name
#         except Exception:
#             # field not present — skip
#             continue

#     # Always include district/state if present (for display)
#     for extra in ('district_fk', 'state'):
#         try:
#             fld = Registration._meta.get_field(extra)
#             if isinstance(fld, (ForeignKey, OneToOneField)):
#                 if extra not in select_related_fields:
#                     select_related_fields.append(extra)
#         except Exception:
#             pass

#     # Build base queryset of registrations that have a bib assigned
#     qs = Registration.objects.filter(bib_id__isnull=False)

#     if select_related_fields:
#         qs = qs.select_related(*select_related_fields)
#     if prefetch_related_fields:
#         qs = qs.prefetch_related(*prefetch_related_fields)

#     # Evaluate queryset (we will annotate in-memory)
#     registrations = list(qs)

#     # Annotate useful display fields for the template
#     today = date.today()
#     for reg in registrations:
#         # age_display (prefer model helper age_on if present)
#         age_val = None
#         age_on = getattr(reg, 'age_on', None)
#         if callable(age_on):
#             try:
#                 age_val = age_on(today)
#             except Exception:
#                 age_val = None
#         if age_val is None:
#             dob = getattr(reg, 'date_of_birth', None)
#             if dob:
#                 age_val = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
#         reg.age_display = str(age_val) if age_val is not None else '—'

#         # public bib without year
#         reg.bib_public = RegistrationBibListView._compute_short_bib(reg.bib_id)

#         # Resolve event_display:
#         event_obj = None
#         # 1) If we have a select_related FK, try those first (skip district/state)
#         for fname in select_related_fields:
#             if fname in ('district_fk', 'state'):
#                 continue
#             event_obj = getattr(reg, fname, None)
#             if event_obj:
#                 break

#         # 2) If not found, check prefetch m2m fields (use all related objects and join names)
#         if event_obj is None and prefetch_related_fields:
#             for fname in prefetch_related_fields:
#                 rel_qs = getattr(reg, fname, None)
#                 # rel_qs may be a manager/queryset; take all() if present
#                 try:
#                     # gather names
#                     names = [getattr(ev, 'name', None) or getattr(ev, 'title', None) or str(ev) for ev in rel_qs.all()]
#                     if names:
#                         event_obj = names  # store as list for joining later
#                         break
#                 except Exception:
#                     # maybe it's already evaluated list-like
#                     try:
#                         names = [getattr(ev, 'name', None) or getattr(ev, 'title', None) or str(ev) for ev in rel_qs]
#                         if names:
#                             event_obj = names
#                             break
#                     except Exception:
#                         pass

#         # 3) If event is stored as plain field on model (string)
#         if event_obj is None and plain_event_field:
#             event_val = getattr(reg, plain_event_field, None)
#             reg.event_display = event_val or '—'
#             continue

#         # 4) If still None, try some common attribute names directly (fallback)
#         if event_obj is None:
#             for attr in ('event', 'race', 'event_name', 'race_name'):
#                 val = getattr(reg, attr, None)
#                 if val:
#                     event_obj = val
#                     break

#         # Now convert event_obj (if present) to a display string
#         if event_obj is None:
#             reg.event_display = '—'
#         else:
#             # If event_obj is a list of names (from M2M), join them
#             if isinstance(event_obj, (list, tuple)):
#                 reg.event_display = ', '.join(event_obj)
#             else:
#                 reg.event_display = getattr(event_obj, 'name', None) or getattr(event_obj, 'title', None) or str(event_obj)

#     context = {
#         'registrations': registrations,
#     }
#     return render(request, 'app_bib/start_list.html', context)


# @staff_member_required
# @require_POST
# def generate_bibs_view(request):
#     """
#     Generate bibs for the current filtered queryset.
#     - Only staff can POST to this.
#     - Accepts a hidden 'qs' POST field containing the current querystring so that
#       filters applied on the list are honoured.
#     """
#     # Reconstruct filter data from POST 'qs' (querystring) if provided
#     qs_string = request.POST.get('qs', '') or ''
#     if qs_string:
#         parsed = parse_qs(qs_string)
#         # parse_qs gives lists for values; RegistrationFilter can accept that shape
#         filter_data = parsed
#     else:
#         filter_data = {}

#     # Build a base queryset (all registrations) and apply the same filterset used by the list view
#     base_qs = Registration.objects.all()
#     try:
#         fs = RegistrationFilter(data=filter_data, queryset=base_qs)
#         filtered_qs = fs.qs
#     except Exception:
#         filtered_qs = base_qs

#     # Narrow to only those without bibs (null or empty)
#     to_generate_qs = filtered_qs.filter(bib_id__isnull=True) | filtered_qs.filter(bib_id__exact='')
#     regs = list(to_generate_qs)

#     generated_count = 0
#     errors = []
#     for reg in regs:
#         try:
#             new_bib = reg.release_bib()
#             # If your model method does not save, uncomment next line:
#             # reg.save()
#             if new_bib:
#                 generated_count += 1
#         except Exception as exc:
#             errors.append(f"{reg.pk}: {exc}")

#     if generated_count:
#         messages.success(request, f"Generated {generated_count} bib(s) for current results.")
#     else:
#         messages.info(request, "No registrations required bib generation (none matched or already have bibs).")

#     if errors:
#         messages.error(request, "Some items failed to generate; check server logs for details.")

#     # Redirect back to list preserving querystring (if present)
#     next_url = request.POST.get('next') or reverse('app_bib:registration_bib_list')
#     if qs_string:
#         redirect_to = f"{next_url}?{qs_string}"
#     else:
#         redirect_to = next_url
#     return redirect(redirect_to)

# def start_list_export_csv(request):
#     """
#     Export the start list as CSV:
#     columns: name, bib number, event, gender, age, start_time, end_time
#     """
#     from io import StringIO
#     import csv
#     from datetime import date
#     from django.db.models import ManyToManyField, ForeignKey, OneToOneField

#     # Build queryset similarly (avoid N+1)
#     select_related_fields = []
#     prefetch_related_fields = []

#     for extra in ('district_fk', 'state'):
#         try:
#             fld = Registration._meta.get_field(extra)
#             if isinstance(fld, (ForeignKey, OneToOneField)):
#                 select_related_fields.append(extra)
#         except Exception:
#             pass

#     try:
#         fld_events = Registration._meta.get_field('events')
#         if isinstance(fld_events, ManyToManyField):
#             prefetch_related_fields.append('events')
#         elif isinstance(fld_events, (ForeignKey, OneToOneField)):
#             select_related_fields.append('events')
#     except Exception:
#         pass

#     qs = Registration.objects.filter(bib_id__isnull=False)
#     if select_related_fields:
#         qs = qs.select_related(*select_related_fields)
#     if prefetch_related_fields:
#         qs = qs.prefetch_related(*prefetch_related_fields)

#     # Prepare CSV
#     output = StringIO()
#     output.write('\ufeff')  # BOM for Excel/Excel-like apps
#     writer = csv.writer(output)

#     writer.writerow(['name', 'bib_number', 'event', 'gender', 'age', 'start_time', 'end_time'])

#     today = date.today()
#     for reg in qs:
#         # name
#         name = getattr(reg, 'name', '') or ''

#         # bib_public if computed on object, else compute here
#         bib_public = getattr(reg, 'bib_public', None)
#         if not bib_public:
#             try:
#                 bib_public = RegistrationBibListView._compute_short_bib(reg.bib_id)
#             except Exception:
#                 bib = getattr(reg, 'bib_id', '')
#                 if not bib:
#                     bib_public = ''
#                 else:
#                     parts = str(bib).split('-')
#                     for i, p in enumerate(parts):
#                         if re.fullmatch(r'\d{4}', p):
#                             parts.pop(i)
#                             bib_public = '-'.join(parts)
#                             break
#                     else:
#                         bib_public = str(bib)

#         # event_display resolution (reuse same logic)
#         event_display = ''
#         events_rel = getattr(reg, 'events', None)
#         if events_rel is not None:
#             try:
#                 names = [getattr(ev, 'name', None) or getattr(ev, 'title', None) or str(ev) for ev in events_rel.all()]
#                 if names:
#                     event_display = ', '.join(names)
#             except Exception:
#                 try:
#                     names = [getattr(ev, 'name', None) or getattr(ev, 'title', None) or str(ev) for ev in events_rel]
#                     if names:
#                         event_display = ', '.join(names)
#                 except Exception:
#                     event_display = ''

#         if not event_display:
#             for attr in ('event_fk', 'event', 'event_name', 'race', 'race_event'):
#                 try:
#                     val = getattr(reg, attr, None)
#                 except Exception:
#                     val = None
#                 if val:
#                     event_display = getattr(val, 'name', None) or getattr(val, 'title', None) or str(val)
#                     break

#         # gender
#         try:
#             gender_display = reg.get_gender_display()
#         except Exception:
#             gender_display = getattr(reg, 'gender', '') or ''

#         # age
#         age_val = ''
#         age_on = getattr(reg, 'age_on', None)
#         if callable(age_on):
#             try:
#                 age_val = age_on(today)
#             except Exception:
#                 age_val = ''
#         if age_val in (None, ''):
#             dob = getattr(reg, 'date_of_birth', None)
#             if dob:
#                 age_val = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

#         start_time = getattr(reg, 'start_time', '') or ''
#         end_time = getattr(reg, 'end_time', '') or ''

#         writer.writerow([name, bib_public, event_display, gender_display, age_val, start_time, end_time])

#     filename = f"start_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#     response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     return response

# @login_required
# def time_entry_list_create(request):
#     if request.method == 'POST':
#         form = TimeEntryForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Time entry saved.")
#             return redirect(reverse('app_bib:time_entry'))
#         else:
#             messages.error(request, "Please fix errors below.")
#     else:
#         form = TimeEntryForm()

#     entries = TimeEntry.objects.all()[:200]  # limit; adjust as needed
#     context = {
#         'form': form,
#         'entries': entries,
#     }
#     return render(request, 'app_bib/time_entry.html', context)


# from datetime import date, datetime
# import re
# import csv
# from io import StringIO
# from .forms import TimeEntryForm
# from django.shortcuts import redirect, get_object_or_404
# from django.urls import reverse
# from django.shortcuts import render
# from django.contrib import messages
# from django.http import HttpResponse
# from django.utils import timezone
# from django.utils.decorators import method_decorator
# from django.contrib.admin.views.decorators import staff_member_required
# from django_filters.views import FilterView

# from accounts.models import Registration
# from django.contrib.auth.decorators import login_required 
# from .filters import RegistrationFilter
# from django.views.decorators.http import require_POST
# from django.apps import apps
# from urllib.parse import parse_qs

# # Cross-app imports
# from app_results.models import Participation 
# TimeEntry = apps.get_model('app_bib', 'TimeEntry')

# @method_decorator(staff_member_required, name='dispatch')
# class RegistrationBibListView(FilterView):
#     model = Registration
#     filterset_class = RegistrationFilter
#     template_name = "app_bib/registration_bib_list.html"
#     paginate_by = 25
#     queryset = Registration.objects.select_related('district_fk', 'state').all()

#     SORT_MAP = {
#         'bib_id': 'bib_id',
#         'district': 'district_fk__name',
#         'gender': 'gender',
#         'age': 'date_of_birth',
#     }
#     DEFAULT_ORDERING = 'bib_id'

#     def get_queryset(self):
#         base_qs = self.queryset
#         filterset = self.filterset_class(self.request.GET or None, queryset=base_qs)
#         qs = filterset.qs
#         sort = self.request.GET.get('sort')
#         if sort:
#             desc = sort.startswith('-')
#             key = sort[1:] if desc else sort
#             field = self.SORT_MAP.get(key)
#             if field:
#                 order_field = f"-{field}" if desc else field
#                 qs = qs.order_by(order_field)
#         else:
#             qs = qs.order_by(self.DEFAULT_ORDERING)
#         return qs

#     def _compute_age_from_dob(self, dob, today=None):
#         if not dob: return None
#         if today is None: today = date.today()
#         return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

#     @staticmethod
#     def _compute_short_bib(bib):
#         if not bib: return "—"
#         parts = str(bib).split('-')
#         for i, p in enumerate(parts):
#             if re.fullmatch(r'\d{4}', p):
#                 parts.pop(i)
#                 return '-'.join(parts)
#         if len(parts) >= 4:
#             parts.pop(3)
#             return '-'.join(parts)
#         return str(bib)

#     def get(self, request, *args, **kwargs):
#         if request.GET.get('export') == 'csv':
#             return self._export_csv_response()
#         return super().get(request, *args, **kwargs)

#     def _export_csv_response(self):
#         qs = self.get_queryset()
#         output = StringIO()
#         output.write('\ufeff')
#         writer = csv.writer(output)
#         writer.writerow(['bib_id', 'bib_public', 'name', 'district', 'age', 'gender', 'bib_released_at'])
#         today = date.today()
#         for reg in qs:
#             bib_public = self._compute_short_bib(reg.bib_id)
#             dob = getattr(reg, 'date_of_birth', None)
#             age_val = self._compute_age_from_dob(dob, today)
#             writer.writerow([
#                 reg.bib_id or '', bib_public, getattr(reg, 'name', '') or '',
#                 reg.district_fk.name if reg.district_fk else '',
#                 age_val if age_val is not None else '',
#                 reg.get_gender_display() if hasattr(reg, 'get_gender_display') else '',
#                 reg.bib_released_at.isoformat() if reg.bib_released_at else '',
#             ])
#         filename = f"bib_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
#         response = HttpResponse(output.getvalue(), content_type='text/csv')
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         return response

#     def get_context_data(self, **kwargs):
#         ctx = super().get_context_data(**kwargs)
#         params = self.request.GET.copy()
#         if 'page' in params: params.pop('page')
#         ctx['current_querystring'] = params.urlencode()
#         ctx['current_sort'] = self.request.GET.get('sort', self.DEFAULT_ORDERING)
#         today = date.today()
#         page_obj = ctx.get('page_obj')
#         if page_obj:
#             for reg in page_obj.object_list:
#                 dob = getattr(reg, 'date_of_birth', None)
#                 age_val = self._compute_age_from_dob(dob, today)
#                 reg.age_display = str(age_val) if age_val is not None else '—'
#                 reg.bib_public = self._compute_short_bib(reg.bib_id)
#         return ctx

# @login_required
# def start_list_view(request):
#     """
#     Displays the Start List with the ability to:
#     1. Toggle attendance (Present/Absent).
#     2. Assign/Change Heats on the fly.
#     """
#     # 1. Fetch registrations with bibs, optimizing queries with select_related
#     registrations = Registration.objects.filter(
#         bib_id__isnull=False
#     ).select_related('race', 'heat', 'participation')

#     # 2. Fetch all heats for the dropdown assignment
#     # You could also filter this by a specific race if needed
#     all_heats = Heat.objects.all()

#     today = date.today()

#     for r in registrations:
#         # Age calculation logic
#         r.age_display = r.age_on(today) if hasattr(r, 'age_on') else "—"
        
#         # Check attendance status from participation model
#         r.is_present = r.participation.is_participated if hasattr(r, 'participation') else False
        
#         # Simple event display logic
#         r.event_display = r.race.name if r.race else "No Race Assigned"

#     context = {
#         'registrations': registrations,
#         'heats': all_heats,
#     }
#     return render(request, 'app_bib/start_list.html', context)


# @staff_member_required
# @require_POST
# def toggle_attendance(request, reg_id):
#     registration = get_object_or_404(Registration, id=reg_id)
#     participation, created = Participation.objects.get_or_create(start_entry=registration)
#     participation.is_participated = not participation.is_participated
#     participation.save()
#     status = "Present" if participation.is_participated else "Absent"
#     messages.success(request, f"{registration.name} marked as {status}.")
#     return redirect('app_bib:start_list')

# @staff_member_required
# @require_POST
# def generate_bibs_view(request):
#     qs_string = request.POST.get('qs', '')
#     filter_data = parse_qs(qs_string) if qs_string else {}
#     base_qs = Registration.objects.all()
#     try:
#         fs = RegistrationFilter(data=filter_data, queryset=base_qs)
#         filtered_qs = fs.qs
#     except:
#         filtered_qs = base_qs
#     to_generate_qs = filtered_qs.filter(bib_id__isnull=True) | filtered_qs.filter(bib_id__exact='')
#     count = 0
#     for reg in to_generate_qs:
#         if reg.release_bib(): count += 1
#     if count: messages.success(request, f"Generated {count} bib(s).")
#     return redirect(reverse('app_bib:registration_bib_list') + (f"?{qs_string}" if qs_string else ""))

# def start_list_export_csv(request):
#     """
#     RESTORED: Full Start List CSV export.
#     """
#     qs = Registration.objects.filter(bib_id__isnull=False).select_related('participation', 'district_fk')
#     output = StringIO()
#     output.write('\ufeff')
#     writer = csv.writer(output)
#     writer.writerow(['Name', 'Bib Number', 'Gender', 'Age', 'Status'])
#     today = date.today()
#     for reg in qs:
#         dob = getattr(reg, 'date_of_birth', None)
#         age = (today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))) if dob else '—'
#         status = "Present" if hasattr(reg, 'participation') and reg.participation.is_participated else "Absent"
#         writer.writerow([reg.name, reg.bib_id, reg.gender, age, status])
#     response = HttpResponse(output.getvalue(), content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="start_list_{datetime.now().strftime("%Y%m%d")}.csv"'
#     return response

# @login_required
# def time_entry_list_create(request):
#     """
#     Live Timing Sheet:
#     - Displays participants marked 'Present' in Start List.
#     - Provides Race-based filtering.
#     - Dynamically calculates Age (with safety fallbacks).
#     """
#     from app_races.models import Race
#     from datetime import date
    
#     # 1. Fetch all races for the dropdown filter
#     races = Race.objects.all()
    
#     # 2. Grab selected race from query params
#     selected_race_id = request.GET.get('race_id')
    
#     # 3. Base Query: Start with 'Present' participants only
#     # Optimized with select_related to prevent database lag
#     qs = Registration.objects.filter(
#         participation__is_participated=True
#     ).select_related('race', 'participation', 'district_fk')

#     # 4. Filter by Race if the user selected one
#     if selected_race_id:
#         qs = qs.filter(race_id=selected_race_id)

#     registrations = list(qs)
#     today = date.today()

#     for reg in registrations:
#         # --- ROBUST AGE LOGIC ---
#         # Try model method first, fallback to manual calculation if method is missing
#         current_age = None
#         if hasattr(reg, 'age_on'):
#             try:
#                 current_age = reg.age_on(today)
#             except:
#                 current_age = None
        
#         # Manual fallback if age_on failed or doesn't exist
#         if current_age is None:
#             dob = getattr(reg, 'date_of_birth', None)
#             if dob:
#                 current_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
#         reg.age_display = current_age if current_age is not None else "—"

#         # --- BIB LOGIC ---
#         # Ensure we use the short-format bib for the UI
#         reg.bib_public = RegistrationBibListView._compute_short_bib(reg.bib_id)
        
#         # --- DATA PREP ---
#         # Pull existing finish time from Participation model
#         reg.current_time = reg.participation.end_time_mmss if hasattr(reg, 'participation') else ""

#     context = {
#         'registrations': registrations,
#         'races': races,
#         'selected_race_id': selected_race_id,
#     }
#     return render(request, 'app_bib/time_entry.html', context)

# @staff_member_required
# @require_POST
# def assign_heat(request, reg_id):
#     registration = get_object_or_404(Registration, id=reg_id)
#     # Get the number from the form
#     new_heat = request.POST.get('heat_id') 
#     registration.heat_number = new_heat if new_heat else None
#     registration.save()
#     return redirect(request.META.get('HTTP_REFERER', 'app_bib:start_list'))

# # app_bib/views.py

# @staff_member_required
# def heat_list_view(request):
#     """
#     Displays participants who are marked 'Present' and allows
#     auto-assignment of heats based on DOB.
#     """
#     selected_race_id = request.GET.get('race_id')
    
#     # 1. Get only those who are marked 'Present' in Participation
#     qs = Registration.objects.filter(
#         participation__is_participated=True,
#         bib_id__isnull=False # Safety check: must have a bib
#     ).select_related('participation', 'district_fk')

#     if selected_race_id:
#         qs = qs.filter(race_id=selected_race_id)

#     # Sort by DOB for display (Oldest to Youngest or vice versa)
#     registrations = qs.order_by('date_of_birth')

#     context = {
#         'registrations': registrations,
#         'selected_race_id': selected_race_id,
#     }
#     return render(request, 'app_bib/heat_list.html', context)

# @staff_member_required
# @require_POST
# def auto_assign_heats(request):
#     """
#     Logic: Take all 'Present' people for a race, sort by DOB, 
#     and assign them to heats (e.g., 10 people per heat).
#     """
#     race_id = request.POST.get('race_id')
#     players_per_heat = int(request.POST.get('size', 10))

#     participants = Registration.objects.filter(
#         race_id=race_id,
#         participation__is_participated=True
#     ).order_by('date_of_birth')

#     heat_counter = 1
#     for index, reg in enumerate(participants):
#         # Every time we hit the 'size' limit, increment the heat number
#         if index > 0 and index % players_per_heat == 0:
#             heat_counter += 1
        
#         reg.heat_number = heat_counter
#         reg.save()

#     messages.success(request, f"Assigned {participants.count()} athletes into {heat_counter} heats.")
#     return redirect(reverse('app_bib:heat_list') + f"?race_id={race_id}")

from datetime import date, datetime
import re
import csv
from io import StringIO

from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required 
from django.views.decorators.http import require_POST
from django.apps import apps
from urllib.parse import parse_qs
from django.db import models
from django.db.models import Q # Crucial for the Gatekeeper logic
from django_filters.views import FilterView

# Internal Imports
from accounts.models import Registration
from .filters import RegistrationFilter
from app_results.models import Participation 

# Using apps.get_model to avoid circular imports
TimeEntry = apps.get_model('app_bib', 'TimeEntry')
Race = apps.get_model('app_races', 'Race')

@method_decorator(staff_member_required, name='dispatch')
class RegistrationBibListView(FilterView):
    model = Registration
    filterset_class = RegistrationFilter
    template_name = "app_bib/registration_bib_list.html"
    paginate_by = 25
    queryset = Registration.objects.select_related('district_fk', 'state', 'participation').all()

    SORT_MAP = {
        'bib_id': 'bib_id',
        'district': 'district_fk__name',
        'gender': 'gender',
        'age': 'date_of_birth',
    }
    DEFAULT_ORDERING = 'bib_id'

    def get_queryset(self):
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
        if not dob: return None
        if today is None: today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @staticmethod
    def _compute_short_bib(bib):
        if not bib: return "—"
        parts = str(bib).split('-')
        for i, p in enumerate(parts):
            if re.fullmatch(r'\d{4}', p):
                parts.pop(i)
                return '-'.join(parts)
        return str(bib)

    def get(self, request, *args, **kwargs):
        if request.GET.get('export') == 'csv':
            return self._export_csv_response()
        return super().get(request, *args, **kwargs)

    def _export_csv_response(self):
        qs = self.get_queryset()
        output = StringIO()
        output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(['bib_id', 'bib_public', 'name', 'district', 'age', 'gender', 'bib_released_at'])
        today = date.today()
        for reg in qs:
            bib_public = self._compute_short_bib(reg.bib_id)
            dob = getattr(reg, 'date_of_birth', None)
            age_val = self._compute_age_from_dob(dob, today)
            writer.writerow([
                reg.bib_id or '', bib_public, getattr(reg, 'name', '') or '',
                reg.district_fk.name if reg.district_fk else '',
                age_val if age_val is not None else '',
                reg.get_gender_display() if hasattr(reg, 'get_gender_display') else '',
                reg.bib_released_at.isoformat() if reg.bib_released_at else '',
            ])
        filename = f"bib_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        if 'page' in params: params.pop('page')
        ctx['current_querystring'] = params.urlencode()
        ctx['current_sort'] = self.request.GET.get('sort', self.DEFAULT_ORDERING)
        today = date.today()
        page_obj = ctx.get('page_obj')
        if page_obj:
            for reg in page_obj.object_list:
                dob = getattr(reg, 'date_of_birth', None)
                age_val = self._compute_age_from_dob(dob, today)
                reg.age_display = str(age_val) if age_val is not None else '—'
                reg.bib_public = self._compute_short_bib(reg.bib_id)
                # Ensure participation is available for the UI toggle
                reg.is_collected = reg.participation.is_collected if hasattr(reg, 'participation') else False
        return ctx

@staff_member_required
@require_POST
def toggle_collection(request, reg_id):
    """
    STEP 1 GATEKEEPER: Marks if the athlete physically collected their bib at the desk.
    """
    registration = get_object_or_404(Registration, id=reg_id)
    participation, created = Participation.objects.get_or_create(start_entry=registration)
    
    participation.is_collected = not participation.is_collected
    participation.save()
    
    status = "Selected" if participation.is_collected else "Pending"
    messages.success(request, f"{registration.name} status updated to: {status}.")
    return redirect(request.META.get('HTTP_REFERER', 'app_bib:registration_bib_list'))

@login_required
def start_list_view(request):
    """
    Displays the Start List for final track-side check-in.
    """
    registrations = Registration.objects.filter(
        bib_id__isnull=False,
        participation__is_collected=True # Only show those who collected bibs
    ).select_related('race', 'participation')

    today = date.today()
    for r in registrations:
        r.age_display = r.age_on(today) if hasattr(r, 'age_on') else "—"
        r.is_present = r.participation.is_participated if hasattr(r, 'participation') else False
        r.event_display = r.race.name if r.race else "No Race Assigned"

    context = {'registrations': registrations}
    return render(request, 'app_bib/start_list.html', context)

@staff_member_required
@require_POST
def toggle_attendance(request, reg_id):
    """
    STEP 3: Final track-side 'Present' toggle.
    """
    registration = get_object_or_404(Registration, id=reg_id)
    participation, created = Participation.objects.get_or_create(start_entry=registration)
    participation.is_participated = not participation.is_participated
    participation.save()
    status = "Present" if participation.is_participated else "Absent"
    messages.success(request, f"{registration.name} marked as {status}.")
    return redirect('app_bib:start_list')

@staff_member_required
def heat_list_view(request):
    """
    STEP 2 GATEKEEPER: Displays ONLY participants who have collected their bib.
    """
    selected_race_id = request.GET.get('race_id')
    
    # Filter: Must have bib AND must be marked as 'is_collected'
    qs = Registration.objects.filter(
        participation__is_collected=True
    ).exclude(
        Q(bib_id__isnull=True) | Q(bib_id__exact='')
    ).select_related('district_fk', 'race', 'participation')

    if selected_race_id:
        qs = qs.filter(race_id=selected_race_id)

    # Sort by DOB for age-based heat generation
    registrations = qs.order_by('date_of_birth')

    context = {
        'registrations': registrations,
        'selected_race_id': selected_race_id,
        'races': Race.objects.all(),
    }
    return render(request, 'app_bib/heat_list.html', context)

@staff_member_required
@require_POST
def auto_assign_heats(request):
    race_id = request.POST.get('race_id')
    players_per_heat = int(request.POST.get('size', 10))

    if not race_id:
        messages.error(request, "Please select a race first.")
        return redirect('app_bib:heat_list')

    # Only assign heats to those who are physically present/collected
    participants = Registration.objects.filter(
        race_id=race_id,
        participation__is_collected=True
    ).order_by('date_of_birth')

    for index, reg in enumerate(participants):
        reg.heat_number = (index // players_per_heat) + 1
        reg.save()

    messages.success(request, f"Assigned {participants.count()} athletes into heats.")
    return redirect(reverse('app_bib:heat_list') + f"?race_id={race_id}")

@login_required
def time_entry_list_create(request):
    """
    Final Stage: Recording results for those at the finish line.
    """
    races = Race.objects.all()
    selected_race_id = request.GET.get('race_id')
    
    qs = Registration.objects.filter(
        participation__is_participated=True
    ).select_related('race', 'participation', 'district_fk')

    if selected_race_id:
        qs = qs.filter(race_id=selected_race_id)

    registrations = list(qs)
    today = date.today()

    for reg in registrations:
        dob = getattr(reg, 'date_of_birth', None)
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day)) if dob else None
        reg.age_display = age if age is not None else "—"
        reg.bib_public = RegistrationBibListView._compute_short_bib(reg.bib_id)
        reg.current_time = reg.participation.end_time_mmss if hasattr(reg, 'participation') else ""

    context = {
        'registrations': registrations,
        'races': races,
        'selected_race_id': selected_race_id,
    }
    return render(request, 'app_bib/time_entry.html', context)

# Manual assignment and exports kept as is...
@staff_member_required
@require_POST
def assign_heat(request, reg_id):
    registration = get_object_or_404(Registration, id=reg_id)
    registration.heat_number = request.POST.get('heat_id') or None
    registration.save()
    return redirect(request.META.get('HTTP_REFERER', 'app_bib:heat_list'))

@staff_member_required
@require_POST
def generate_bibs_view(request):
    qs_string = request.POST.get('qs', '')
    filter_data = parse_qs(qs_string) if qs_string else {}
    base_qs = Registration.objects.all()
    try:
        fs = RegistrationFilter(data=filter_data, queryset=base_qs)
        filtered_qs = fs.qs
    except:
        filtered_qs = base_qs
    to_generate_qs = filtered_qs.filter(Q(bib_id__isnull=True) | Q(bib_id__exact=''))
    count = 0
    for reg in to_generate_qs:
        if reg.release_bib(): count += 1
    if count: messages.success(request, f"Generated {count} bib(s).")
    return redirect(reverse('app_bib:registration_bib_list') + (f"?{qs_string}" if qs_string else ""))


@staff_member_required
def start_list_export_csv(request):
    """
    Export the full Start List to CSV.
    """
    qs = Registration.objects.filter(
        bib_id__isnull=False,
        participation__is_collected=True
    ).select_related('participation', 'district_fk')
    
    output = StringIO()
    output.write('\ufeff')  # UTF-8 BOM for Excel
    writer = csv.writer(output)
    writer.writerow(['Name', 'Bib Number', 'Gender', 'Age', 'Status', 'Heat'])
    
    today = date.today()
    for reg in qs:
        dob = getattr(reg, 'date_of_birth', None)
        age = (today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))) if dob else '—'
        status = "Present" if hasattr(reg, 'participation') and reg.participation.is_participated else "Absent"
        
        writer.writerow([
            reg.name, 
            reg.bib_id, 
            reg.get_gender_display() if hasattr(reg, 'get_gender_display') else reg.gender, 
            age, 
            status,
            reg.heat_number or '—'
        ])
        
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="start_list_{datetime.now().strftime("%Y%m%d")}.csv"'
    return response