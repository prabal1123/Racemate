# app_admin/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import models as djmodels
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
import csv

from accounts.models import Registration
from .forms import RegistrationForm
from app_admin.models import DimState, DimDistrict, DimEventCategory


# ------------------------------
# Admin CRUD views
# ------------------------------

@login_required
def registration_list(request):
    """
    Display all registrations in a simple table.
    """
    registrations = Registration.objects.all()
    return render(request, 'app_admin/registration_list.html', {
        'registrations': registrations
    })


@login_required
def registration_edit(request, pk):
    """
    Edit an existing registration. 
    Includes proper handling of files and ManyToMany fields (events).
    """
    reg = get_object_or_404(Registration, pk=pk)

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES, instance=reg)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.save()
            form.save_m2m()
            messages.success(request, "Registration updated successfully!")
            return redirect('registration_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm(instance=reg)

    return render(request, 'app_admin/registration_edit.html', {
        'form': form,
        'reg': reg,
    })


@login_required
def registration_delete(request, pk):
    """
    Delete a registration after confirmation.
    """
    reg = get_object_or_404(Registration, pk=pk)
    if request.method == 'POST':
        reg.delete()
        messages.success(request, "Registration deleted successfully.")
        return redirect('registration_list')
    return render(request, 'app_admin/registration_confirm_delete.html', {
        'reg': reg
    })


# ------------------------------
# Filtering helper for analysis
# ------------------------------

def build_filtered_qs(request):
    """
    Returns filtered queryset of Registration based on GET params.
    """
    qs = Registration.objects.all()

    # Date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        d = parse_date(date_from)
        if d:
            qs = qs.filter(created_at__date__gte=d)
    if date_to:
        d = parse_date(date_to)
        if d:
            qs = qs.filter(created_at__date__lte=d)

    # State filter (multi)
    state_ids = request.GET.getlist('state')
    if state_ids:
        qs = qs.filter(state_id__in=state_ids)

    # Event filter (multi)
    event_ids = request.GET.getlist('event')
    if event_ids:
        qs = qs.filter(events__in=event_ids)

    # Profession filter
    profession = request.GET.get('profession')
    if profession:
        qs = qs.filter(profession=profession)

    # Gender filter (multi)
    gender_vals = request.GET.getlist('gender')
    if gender_vals:
        qs = qs.filter(gender__in=gender_vals)

    # Quick search (name or mobile)
    search = request.GET.get('q')
    if search:
        qs = qs.filter(
            djmodels.Q(name__icontains=search) |
            djmodels.Q(mobile_number__icontains=search)
        )

    return qs.distinct()


# ------------------------------
# Analysis / Reporting Views
# ------------------------------

@staff_member_required
def api_analysis_summary(request):
    """
    Returns analysis summary JSON:
      - total registrations
      - by_state
      - by_event
      - by_gender
      - by_category (age group)
      - breakdown (category + event + gender)
      - daily series
    """
    qs = build_filtered_qs(request)

    total = qs.count()

    # By State
    by_state_qs = qs.values('state__id', 'state__name').annotate(count=Count('id')).order_by('-count')
    by_state = [{'id': r['state__id'], 'name': r['state__name'] or 'Unknown', 'count': r['count']} for r in by_state_qs]

    # By Event
    by_event_qs = qs.values('events__id', 'events__name').annotate(count=Count('id')).order_by('-count')
    by_event = [{'id': r['events__id'], 'name': r['events__name'] or 'Unknown', 'count': r['count']} for r in by_event_qs]

    # By Gender
    by_gender_qs = qs.values('gender').annotate(count=Count('id')).order_by('gender')
    by_gender = [{'gender': r['gender'] or 'Unspecified', 'count': r['count']} for r in by_gender_qs]

    # By Category (age group)
    by_category_qs = qs.values('category').annotate(count=Count('id')).order_by('category')
    by_category = [{'age_group': r['category'] or 'Unspecified', 'count': r['count']} for r in by_category_qs]

    # Detailed Breakdown (category + event + gender)
    breakdown_qs = (
        qs.values('category', 'events__name', 'gender')
        .annotate(count=Count('id'))
        .order_by('category', 'events__name', 'gender')
    )
    breakdown = [
        {
            'age_group': r['category'] or 'Unspecified',
            'event': r['events__name'] or 'Unspecified',
            'gender': r['gender'] or 'Unspecified',
            'count': r['count'],
        }
        for r in breakdown_qs
    ]

    # Daily time series
    series_qs = qs.annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).order_by('day')
    series = [{'day': r['day'].isoformat(), 'count': r['count']} for r in series_qs if r['day']]

    return JsonResponse({
        'total': total,
        'by_state': by_state,
        'by_event': by_event,
        'by_gender': by_gender,
        'by_category': by_category,
        'series': series,
        'breakdown': breakdown,
    })


@staff_member_required
def analysis_export_csv(request):
    """
    Export filtered registrations to CSV for admin users.
    """
    qs = build_filtered_qs(request).prefetch_related('events').select_related('state', 'district_fk').order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registrations.csv"'
    writer = csv.writer(response)
    writer.writerow(['id', 'name', 'gender', 'mobile', 'state', 'district', 'events', 'category', 'created_at'])

    for r in qs.iterator():
        events = "; ".join(e.name for e in r.events.all())
        writer.writerow([
            r.id,
            r.name,
            r.gender or '',
            r.mobile_number,
            r.state.name if r.state else '',
            r.district_fk.name if r.district_fk else '',
            events,
            r.category or '',
            r.created_at.strftime('%Y-%m-%d %H:%M:%S') if r.created_at else ''
        ])
    return response


@staff_member_required
def analysis_dashboard(request):
    """
    Render analysis dashboard template with filter data.
    """
    states = DimState.objects.all().order_by('name')
    events = DimEventCategory.objects.all().order_by('name')
    professions = [p[0] for p in Registration.PROFESSION_CHOICES]

    # Gender list
    try:
        genders = [{'value': g[0], 'label': g[1]} for g in Registration.GENDER_CHOICES]
    except Exception:
        genders = [
            {'value': 'M', 'label': 'Male'},
            {'value': 'F', 'label': 'Female'},
            {'value': 'O', 'label': 'Other'},
            {'value': '', 'label': 'Unspecified'},
        ]

    return render(request, 'accounts/analysis.html', {
        'states': states,
        'events': events,
        'professions': professions,
        'genders': genders,
    })

