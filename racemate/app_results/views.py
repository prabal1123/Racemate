
# from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse, HttpResponseBadRequest
# from django.views.decorators.http import require_POST
# from django.contrib.admin.views.decorators import staff_member_required
# from django.db.models import Sum
# from django.utils.dateparse import parse_datetime
# from django.apps import apps
# from datetime import timedelta

# from .models import Participation

# # registration model
# Registration = apps.get_model("accounts", "Registration")


# # Try to find lap model automatically
# def find_lap_model():
#     for appcfg in apps.get_app_configs():
#         for m in appcfg.get_models():
#             if m.__name__.lower() == "lap":
#                 return m
#     return None


# def _format_timedelta_for_display(td):
#     """Return H:MM:SS or M:SS human readable string for a timedelta."""
#     if td is None:
#         return None
#     total = int(td.total_seconds())
#     hours, rem = divmod(total, 3600)
#     minutes, seconds = divmod(rem, 60)
#     if hours:
#         return f"{hours}:{minutes:02d}:{seconds:02d}"
#     return f"{minutes}:{seconds:02d}"


# def _parse_mmss_to_timedelta(mmss_str):
#     """
#     Accept "MM:SS", "M:SS", or "H:MM:SS" and return timedelta.
#     Return None if invalid.
#     """
#     if not mmss_str or not isinstance(mmss_str, str):
#         return None
#     s = mmss_str.strip()
#     parts = s.split(":")
#     try:
#         if len(parts) == 2:
#             minutes = int(parts[0])
#             seconds = int(parts[1])
#             if minutes < 0 or seconds < 0 or seconds >= 60:
#                 return None
#             return timedelta(minutes=minutes, seconds=seconds)
#         elif len(parts) == 3:
#             hours = int(parts[0])
#             minutes = int(parts[1])
#             seconds = int(parts[2])
#             if hours < 0 or minutes < 0 or minutes >= 60 or seconds < 0 or seconds >= 60:
#                 return None
#             return timedelta(hours=hours, minutes=minutes, seconds=seconds)
#     except (ValueError, TypeError):
#         return None
#     return None


# @staff_member_required
# def results_list(request):
#     entries = Registration.objects.all().select_related("participation")
#     LapModel = find_lap_model()

#     # Attach computed lap time
#     for e in entries:
#         e.total_lap_time = None
#         if LapModel:
#             try:
#                 # try FK named 'registration' or 'start_entry'
#                 if hasattr(LapModel, 'registration'):
#                     e.total_lap_time = LapModel.objects.filter(registration=e).aggregate(total=Sum('duration'))['total']
#                 elif hasattr(LapModel, 'start_entry'):
#                     e.total_lap_time = LapModel.objects.filter(start_entry=e).aggregate(total=Sum('duration'))['total']
#             except Exception:
#                 e.total_lap_time = None

#         # fallback to participation value if aggregate is empty
#         if not e.total_lap_time and getattr(e, "participation", None):
#             e.total_lap_time = e.participation.total_lap_time

#     return render(request, "app_results/results_list.html", {"entries": entries})


# @require_POST
# @staff_member_required
# def update_participation(request, start_entry_id):
#     import json

#     try:
#         payload = json.loads(request.body.decode("utf-8") or "{}")
#     except Exception:
#         return HttpResponseBadRequest("Invalid JSON")

#     entry = get_object_or_404(Registration, pk=start_entry_id)
#     participation, created = Participation.objects.get_or_create(start_entry=entry)

#     # Auto-fill category (age_group) from Registration
#     participation.age_group = (
#         getattr(entry, "category", None)
#         or getattr(entry, "age_category", None)
#         or ""
#     )

#     # Auto-fill gender only when first created
#     if created:
#         participation.gender = getattr(entry, "gender", "")

#     # Toggle participated
#     if "is_participated" in payload:
#         participation.is_participated = bool(payload["is_participated"])

#     # Allow editing gender (optional) - accept null to keep, empty to clear
#     if "gender" in payload:
#         g = payload.get("gender")
#         if g is not None:
#             participation.gender = g or ""

#     # End time: accept new key end_time_mmss (MM:SS or H:MM:SS)
#     if "end_time_mmss" in payload:
#         et_val = payload.get("end_time_mmss")
#         if et_val is None or et_val == "":
#             participation.end_time_mmss = None
#         else:
#             td = _parse_mmss_to_timedelta(str(et_val))
#             if td is not None:
#                 # store normalized string (M:SS or H:MM:SS)
#                 hours, rem = divmod(int(td.total_seconds()), 3600)
#                 minutes, seconds = divmod(rem, 60)
#                 participation.end_time_mmss = f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"
#             else:
#                 # invalid format → ignore
#                 pass

#     # Backwards-compatible: also support previous 'end_time' ISO if present
#     if "end_time" in payload:
#         et = payload.get("end_time")
#         if et:
#             dt = parse_datetime(et)
#             if dt:
#                 # if dt parsed, convert its time-of-day to mm:ss (or total minutes)
#                 mins = dt.hour * 60 + dt.minute
#                 secs = dt.second
#                 participation.end_time_mmss = f"{mins}:{secs:02d}"
#             else:
#                 # ignore invalid
#                 pass
#         else:
#             participation.end_time_mmss = None

#     # Lap seconds → Duration
#     if "total_lap_time_seconds" in payload:
#         secs_val = payload.get("total_lap_time_seconds")
#         if secs_val is None or secs_val == "":
#             participation.total_lap_time = None
#         else:
#             try:
#                 secs = float(secs_val)
#                 participation.total_lap_time = timedelta(seconds=secs)
#             except Exception:
#                 # parsing failed -> leave existing value
#                 pass

#     participation.save()

#     # Prepare response values
#     total_seconds = None
#     total_display = None
#     if participation.total_lap_time is not None:
#         total_seconds = participation.total_lap_time.total_seconds()
#         total_display = _format_timedelta_for_display(participation.total_lap_time)

#     return JsonResponse({
#         "ok": True,
#         "age_group": participation.age_group,
#         "gender": participation.gender,
#         "is_participated": participation.is_participated,
#         "total_lap_time_seconds": total_seconds,
#         "total_lap_time_display": total_display,
#         "end_time_mmss": participation.end_time_mmss,
#     })





# app_results/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.utils.dateparse import parse_datetime
from django.apps import apps
from datetime import timedelta

from .models import Participation

# registration model
Registration = apps.get_model("accounts", "Registration")


# Try to find lap model automatically
def find_lap_model():
    for appcfg in apps.get_app_configs():
        for m in appcfg.get_models():
            if m.__name__.lower() == "lap":
                return m
    return None


def _format_timedelta_for_display(td):
    """Return H:MM:SS or M:SS human readable string for a timedelta."""
    if td is None:
        return None
    total = int(td.total_seconds())
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _parse_mmss_to_timedelta(mmss_str):
    """
    Accept "MM:SS", "M:SS", or "H:MM:SS" and return timedelta.
    Return None if invalid.
    """
    if not mmss_str or not isinstance(mmss_str, str):
        return None
    s = mmss_str.strip()
    parts = s.split(":")
    try:
        if len(parts) == 2:
            minutes = int(parts[0])
            seconds = int(parts[1])
            if minutes < 0 or seconds < 0 or seconds >= 60:
                return None
            return timedelta(minutes=minutes, seconds=seconds)
        elif len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            if hours < 0 or minutes < 0 or minutes >= 60 or seconds < 0 or seconds >= 60:
                return None
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except (ValueError, TypeError):
        return None
    return None


@staff_member_required
def results_list(request):
    """
    Render results / participation list.

    Attaches safe attributes to each Registration instance so the template can
    simply render `entry.category_display`, `entry.gender_display`, and
    `entry.total_lap_time_display` without risking VariableDoesNotExist.
    """

    # load registrations and prefetch/select related participation to avoid N+1
    entries_qs = Registration.objects.all().select_related("participation")

    LapModel = find_lap_model()

    # evaluate into list so we can attach attributes safely
    entries = list(entries_qs)

    for e in entries:
        # --- compute total_lap_time (timedelta) if LapModel exists ---
        e.total_lap_time = None
        if LapModel:
            try:
                # prefer relationships named 'registration' or 'start_entry'
                if hasattr(LapModel, 'registration'):
                    agg = LapModel.objects.filter(registration=e).aggregate(total=Sum('duration'))
                    e.total_lap_time = agg.get('total')
                elif hasattr(LapModel, 'start_entry'):
                    agg = LapModel.objects.filter(start_entry=e).aggregate(total=Sum('duration'))
                    e.total_lap_time = agg.get('total')
            except Exception:
                e.total_lap_time = None

        # fallback to participation value if aggregate is empty
        try:
            if (not e.total_lap_time) and getattr(e, "participation", None):
                e.total_lap_time = getattr(e.participation, "total_lap_time", None)
        except Exception:
            pass

        # Attach display string for lap time
        try:
            e.total_lap_time_display = _format_timedelta_for_display(e.total_lap_time)
        except Exception:
            e.total_lap_time_display = None

        # --- compute category_display robustly ---
        display_cat = '—'
        try:
            part = getattr(e, 'participation', None)
            if part:
                ag = getattr(part, 'age_group', None)
                if ag:
                    display_cat = ag
                    e.category_display = display_cat
                    # ensure participation remains attached
                    e.participation = part
                    # continue to next entry
                    continue
        except Exception:
            # ignore and fall back
            pass

        try:
            cat = getattr(e, 'category', None)
            if cat:
                display_cat = cat
                e.category_display = display_cat
                continue
        except Exception:
            pass

        try:
            age_cat = getattr(e, 'age_category', None)
            if age_cat:
                display_cat = age_cat
                e.category_display = display_cat
                continue
        except Exception:
            pass

        e.category_display = display_cat

        # --- compute gender_display safely ---
        try:
            gfunc = getattr(e, 'get_gender_display', None)
            if callable(gfunc):
                e.gender_display = gfunc()
            else:
                e.gender_display = getattr(e, 'gender', '') or ''
        except Exception:
            e.gender_display = getattr(e, 'gender', '') or ''

    # render
    return render(request, "app_results/results_list.html", {"entries": entries})


@require_POST
@staff_member_required
def update_participation(request, start_entry_id):
    import json

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    entry = get_object_or_404(Registration, pk=start_entry_id)
    participation, created = Participation.objects.get_or_create(start_entry=entry)

    # Auto-fill category (age_group) from Registration
    participation.age_group = (
        getattr(entry, "category", None)
        or getattr(entry, "age_category", None)
        or ""
    )

    # Auto-fill gender only when first created
    if created:
        participation.gender = getattr(entry, "gender", "")

    # Toggle participated
    if "is_participated" in payload:
        participation.is_participated = bool(payload["is_participated"])

    # Allow editing gender (optional) - accept null to keep, empty to clear
    if "gender" in payload:
        g = payload.get("gender")
        if g is not None:
            participation.gender = g or ""

    # End time: accept new key end_time_mmss (MM:SS or H:MM:SS)
    if "end_time_mmss" in payload:
        et_val = payload.get("end_time_mmss")
        if et_val is None or et_val == "":
            participation.end_time_mmss = None
        else:
            td = _parse_mmss_to_timedelta(str(et_val))
            if td is not None:
                # store normalized string (M:SS or H:MM:SS)
                hours, rem = divmod(int(td.total_seconds()), 3600)
                minutes, seconds = divmod(rem, 60)
                participation.end_time_mmss = f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"
            else:
                # invalid format → ignore
                pass

    # Backwards-compatible: also support previous 'end_time' ISO if present
    if "end_time" in payload:
        et = payload.get("end_time")
        if et:
            dt = parse_datetime(et)
            if dt:
                # if dt parsed, convert its time-of-day to mm:ss (or total minutes)
                mins = dt.hour * 60 + dt.minute
                secs = dt.second
                participation.end_time_mmss = f"{mins}:{secs:02d}"
            else:
                # ignore invalid
                pass
        else:
            participation.end_time_mmss = None

    # Lap seconds → Duration
    if "total_lap_time_seconds" in payload:
        secs_val = payload.get("total_lap_time_seconds")
        if secs_val is None or secs_val == "":
            participation.total_lap_time = None
        else:
            try:
                secs = float(secs_val)
                participation.total_lap_time = timedelta(seconds=secs)
            except Exception:
                # parsing failed -> leave existing value
                pass

    participation.save()

    # Prepare response values
    total_seconds = None
    total_display = None
    if participation.total_lap_time is not None:
        total_seconds = participation.total_lap_time.total_seconds()
        total_display = _format_timedelta_for_display(participation.total_lap_time)

    return JsonResponse({
        "ok": True,
        "age_group": participation.age_group,
        "gender": participation.gender,
        "is_participated": participation.is_participated,
        "total_lap_time_seconds": total_seconds,
        "total_lap_time_display": total_display,
        "end_time_mmss": participation.end_time_mmss,
    })
