

from .forms import UserProfileForm
# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.utils.safestring import mark_safe
from django.db.models import Q
from app_races.models import Race, Event, RaceRegistration
from django.contrib.auth.models import User
from django import forms

from .models import Registration
from .forms import RegistrationForm, PublicRegistrationForm
from app_admin.models import DimDistrict, DimState
from django.shortcuts import render
from .models import Profile
from app_races.models import Race
from django.utils import timezone

# --- Tournament module imports (Phase 1) ---
from app_tournaments.models import (
    Tournament,
    TournamentCategory,
    TournamentEntry,
    TournamentEntryPlayer,
    EntryStatus,
)
from .tournament_helpers import get_or_create_user_for_registration
from app_tournaments.models import Tournament


# def home(request):
#     """
#     Homepage:
#     - Cycling races
#     - Badminton tournaments
#     - Pickleball tournaments
#     - Upcoming + past events
#     """

#     now = timezone.now()
    

#     # ============================================================
#     # CYCLING RACES
#     # ============================================================

#     db_races = (
#         Race.objects
#         .all()
#         .prefetch_related(
#             "race_registrations",
#             "events",
#         )
#         .order_by("race_start")
#     )

#     # ============================================================
#     # BADMINTON / PICKLEBALL TOURNAMENTS
#     # ============================================================

#     db_tournaments = (
#         Tournament.objects
#         .select_related("sport")
#         .prefetch_related(
#             "categories__category",
#             "categories__entry_format",
#             "categories__entries",
#         )
#         .order_by("tournament_start")
#     )

#     upcoming_events = []
#     past_events = []

#     # ============================================================
#     # CONVERT CYCLING RACES INTO COMMON EVENT FORMAT
#     # ============================================================

#     for race in db_races:

#         categories = []

#         for race_event in race.events.all():

#             suffix = ""

#             if race_event.distance_km:
#                 suffix = f"{race_event.distance_km}km"

#             categories.append({
#                 "label": race_event.title,
#                 "suffix": suffix,
#             })

#         race_data = {
#             "name": race.name,
#             "sport": "cycling",
#             "start": race.race_start,
#             "location": race.location,

#             "participant_count": (
#                 race.race_registrations.count()
#             ),

#             "categories": categories,
#             "status": race.status,

#             "register_query": (
#                 f"race_id={race.id}"
#             ),

#             "winners": [],

#             # Cycling result page
#             "results_url": (
#                 reverse("app_results:list")
#                 + f"?race_id={race.id}"
#             ),

#             # Tournaments use this instead
#             "result_links": [],
#         }

#         # Upcoming / currently active race
#         if (
#             race.status == "LIVE NOW"
#             or race.status == "REGISTRATION OPEN"
#             or race.race_start >= now
#         ):
#             upcoming_events.append(race_data)

#         else:
#             past_events.append(race_data)

#     # ============================================================
#     # CONVERT BADMINTON / PICKLEBALL TOURNAMENTS
#     # ============================================================

#     for tournament in db_tournaments:

#         sport_name = (
#             tournament.sport.name
#             .strip()
#             .lower()
#         )

#         # Only sports currently shown on this homepage
#         if sport_name not in [
#             "badminton",
#             "pickleball",
#         ]:
#             continue

#         categories = []

#         participant_count = 0

#         result_links = []

#         for tournament_category in tournament.categories.all():

#             # Ignore inactive categories
#             if not tournament_category.is_active:
#                 continue

#             categories.append({
#                 "label": tournament_category.category.name,

#                 "suffix": (
#                     tournament_category.entry_format.name
#                     if tournament_category.entry_format
#                     else ""
#                 ),
#             })
#             result_links.append({
#                 "label": tournament_category.category.name,

#                 "url": reverse(
#                     "app_tournaments:results",
#                     kwargs={
#                         "object_id": tournament_category.id
#                     }
#                 ),
#             })
            

#             participant_count += (
#                 tournament_category.entries.count()
#             )

#         tournament_start_date = (
#             timezone.localtime(
#                 tournament.tournament_start
#             ).date()
#         )

#         tournament_data = {
#             "name": tournament.name,

#             "sport": sport_name,

#             "start": tournament.tournament_start,

#             "location": tournament.venue,

#             "participant_count": participant_count,

#             "categories": categories,

#             "status": tournament.status,

#             "register_query": (
#                 f"tournament_id={tournament.id}"
#             ),

#             "winners": [],

#             "results_url": "",

#             "result_links": result_links,
#         }

#         # Tournament is upcoming or currently live
#         if (
#             tournament.status == "LIVE NOW"
#             or tournament.tournament_start >= now
#         ):
#             upcoming_events.append(
#                 tournament_data
#             )

#         else:
#             past_events.append(
#                 tournament_data
#             )

#     # ============================================================
#     # SORT ALL SPORTS TOGETHER
#     # ============================================================

#     upcoming_events.sort(
#         key=lambda event: event["start"]
#     )

#     past_events.sort(
#         key=lambda event: event["start"],
#         reverse=True,
#     )

#     # ============================================================
#     # EXISTING DUMMY RESULTS
#     # ============================================================

#     recent_results = [
#         {
#             "event": "Table Mountain Time Trial",
#             "date": "Feb 28, 2026",
#             "results": [
#                 {
#                     "name": "Liam Jacobs",
#                     "time": "2h 14m 32s",
#                 },
#                 {
#                     "name": "Thabo Molefe",
#                     "time": "2h 16m 08s",
#                 },
#                 {
#                     "name": "Sarah van Niekerk",
#                     "time": "2h 18m 45s",
#                 },
#             ],
#         },
#         {
#             "event": "Winelands Classic",
#             "date": "Feb 15, 2026",
#             "results": [
#                 {
#                     "name": "Nina Botha",
#                     "time": "3h 02m 11s",
#                 },
#                 {
#                     "name": "Chris Dlamini",
#                     "time": "3h 04m 50s",
#                 },
#                 {
#                     "name": "James Le Roux",
#                     "time": "3h 07m 22s",
#                 },
#             ],
#         },
#         {
#             "event": "Midlands Meander MTB",
#             "date": "Jan 25, 2026",
#             "results": [
#                 {
#                     "name": "Ethan Pretorius",
#                     "time": "4h 31m 09s",
#                 },
#                 {
#                     "name": "Zanele Nkosi",
#                     "time": "4h 35m 44s",
#                 },
#                 {
#                     "name": "Pieter du Toit",
#                     "time": "4h 38m 01s",
#                 },
#             ],
#         },
#     ]

#     # ============================================================
#     # TEMPLATE CONTEXT
#     # ============================================================

#     context = {
#         "races": db_races,

#         # These are what your new template uses
#         "upcoming_events": upcoming_events,
#         "past_events": past_events,

#         "recent_results": recent_results,
#         "now": now,
#     }

#     return render(
#         request,
#         "accounts/home.html",
#         context,
#     )

def home(request):
    """
    Homepage:
    - Cycling races
    - Badminton tournaments
    - Pickleball tournaments
    - Upcoming + past events
    """

    now = timezone.now()


    # ============================================================
    # CYCLING RACES
    # ============================================================

    db_races = (
        Race.objects
        .all()
        .prefetch_related(
            "race_registrations",
            "events",
        )
        .order_by("race_start")
    )

    # ============================================================
    # BADMINTON / PICKLEBALL TOURNAMENTS
    # ============================================================

    db_tournaments = (
        Tournament.objects
        .select_related("sport")
        .prefetch_related(
            "categories__category",
            "categories__entry_format",
            "categories__entries",
        )
        .order_by("tournament_start")
    )

    upcoming_events = []
    past_events = []

    # ============================================================
    # CONVERT CYCLING RACES INTO COMMON EVENT FORMAT
    # ============================================================

    for race in db_races:

        categories = []

        for race_event in race.events.all():

            suffix = ""

            if race_event.distance_km:
                suffix = f"{race_event.distance_km}km"

            categories.append({
                "label": race_event.title,
                "suffix": suffix,
            })

        race_data = {
            "name": race.name,
            "sport": "cycling",
            "start": race.race_start,
            "location": race.location,

            "participant_count": (
                race.race_registrations.count()
            ),

            "categories": categories,
            "status": race.status,

            # One scoped registration link per event in this race —
            # replaces the old single "register_query" (race_id=X)
            # which pointed at the now-removed generic /register/ page.
                        # One scoped registration link per event TYPE used by this
            # race (e.g. "Road Cycling" vs "Track Cycling"), rather than
            # one link per individual event. Only types with at least
            # one categorized Event show up here.
            "registration_links": [
                {
                    "label": event_type.name,
                    "url": race.registration_path_for_type(event_type.id),
                }
                for event_type in race.available_event_types()
            ],

            "winners": [],

            # Cycling result page
            "results_url": (
                reverse("app_results:list")
                + f"?race_id={race.id}"
            ),

            # Tournaments use this instead
            "result_links": [],
        }

        # Upcoming / currently active race
        if (
            race.status == "LIVE NOW"
            or race.status == "REGISTRATION OPEN"
            or race.race_start >= now
        ):
            upcoming_events.append(race_data)

        else:
            past_events.append(race_data)

    # ============================================================
    # CONVERT BADMINTON / PICKLEBALL TOURNAMENTS
    # ============================================================

    for tournament in db_tournaments:

        sport_name = (
            tournament.sport.name
            .strip()
            .lower()
        )

        # Only sports currently shown on this homepage
        if sport_name not in [
            "badminton",
            "pickleball",
        ]:
            continue

        categories = []

        participant_count = 0

        result_links = []

        # One scoped registration link per open category in this
        # tournament — replaces the old single "register_query"
        # (tournament_id=X) which pointed at the removed generic
        # /register/ page.
                # One tournament-level registration link, shown only if at
        # least one category is currently active and open. Replaces
        # the old per-category links list.
        has_open_category = False

        for tournament_category in tournament.categories.all():

            # Ignore inactive categories
            if not tournament_category.is_active:
                continue

            categories.append({
                "label": tournament_category.category.name,

                "suffix": (
                    tournament_category.entry_format.name
                    if tournament_category.entry_format
                    else ""
                ),
            })
            result_links.append({
                "label": tournament_category.category.name,

                "url": reverse(
                    "app_tournaments:results",
                    kwargs={
                        "object_id": tournament_category.id
                    }
                ),
            })

            if tournament_category.registration_open:
                has_open_category = True

            participant_count += (
                tournament_category.entries.count()
            )

        registration_links = (
            [{
                "label": "Register",
                "url": tournament.registration_path(),
            }]
            if has_open_category
            else []
        )

        tournament_start_date = (
            timezone.localtime(
                tournament.tournament_start
            ).date()
        )

        tournament_data = {
            "name": tournament.name,

            "sport": sport_name,

            "start": tournament.tournament_start,

            "location": tournament.venue,

            "participant_count": participant_count,

            "categories": categories,

            "status": tournament.status,

            "registration_links": registration_links,

            "winners": [],

            "results_url": "",

            "result_links": result_links,
        }

        # Tournament is upcoming or currently live
        if (
            tournament.status == "LIVE NOW"
            or tournament.tournament_start >= now
        ):
            upcoming_events.append(
                tournament_data
            )

        else:
            past_events.append(
                tournament_data
            )

    # ============================================================
    # SORT ALL SPORTS TOGETHER
    # ============================================================

    upcoming_events.sort(
        key=lambda event: event["start"]
    )

    past_events.sort(
        key=lambda event: event["start"],
        reverse=True,
    )

    # ============================================================
    # EXISTING DUMMY RESULTS
    # ============================================================

    recent_results = [
        {
            "event": "Table Mountain Time Trial",
            "date": "Feb 28, 2026",
            "results": [
                {
                    "name": "Liam Jacobs",
                    "time": "2h 14m 32s",
                },
                {
                    "name": "Thabo Molefe",
                    "time": "2h 16m 08s",
                },
                {
                    "name": "Sarah van Niekerk",
                    "time": "2h 18m 45s",
                },
            ],
        },
        {
            "event": "Winelands Classic",
            "date": "Feb 15, 2026",
            "results": [
                {
                    "name": "Nina Botha",
                    "time": "3h 02m 11s",
                },
                {
                    "name": "Chris Dlamini",
                    "time": "3h 04m 50s",
                },
                {
                    "name": "James Le Roux",
                    "time": "3h 07m 22s",
                },
            ],
        },
        {
            "event": "Midlands Meander MTB",
            "date": "Jan 25, 2026",
            "results": [
                {
                    "name": "Ethan Pretorius",
                    "time": "4h 31m 09s",
                },
                {
                    "name": "Zanele Nkosi",
                    "time": "4h 35m 44s",
                },
                {
                    "name": "Pieter du Toit",
                    "time": "4h 38m 01s",
                },
            ],
        },
    ]

    # ============================================================
    # TEMPLATE CONTEXT
    # ============================================================

    context = {
        "races": db_races,

        # These are what your new template uses
        "upcoming_events": upcoming_events,
        "past_events": past_events,

        "recent_results": recent_results,
        "now": now,
    }

    return render(
        request,
        "accounts/home.html",
        context,
    )


@login_required
def check_profile_completion(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if not user.first_name or not user.last_name or not profile.phone_number:
        messages.info(request, "Almost there! Please complete your profile details.")
        return redirect('accounts:profile_edit')

    return redirect('accounts:profile')


def _attach_partner_position_ranges(tournaments_qs):
    """
    For each category under each tournament, attach a `partner_positions`
    attribute (a plain list, not stored in DB) so register.html can render
    partner slots server-side without needing an AJAX call or a custom
    template tag. E.g. a Doubles category (max_players=2) gets
    partner_positions = [2]; a 4-player Team category gets [2, 3, 4].
    Singles (max_players=1) gets an empty list, so no slots render.
    """
    for tournament in tournaments_qs:
        for category in tournament.categories.all():
            max_players = category.entry_format.maximum_players
            category.partner_positions = list(range(2, max_players + 1))

def register_race_event(request, event_uuid):
    """
    Public, single-event registration page: /register/event/<uuid>/

    Which event a participant registers for is determined ONLY by
    event_uuid from the URL - never from posted form data. No race
    picker, no event checkboxes: the event is fixed by the link.
    """
    event = get_object_or_404(
        Event.objects.select_related("race"),
        uuid=event_uuid,
    )
    race = event.race

    if request.method == "POST":
        form = PublicRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            reg = form.save(commit=False)
            reg.registration_type = "race"
            reg.race = race
            reg.save()
            form.save_m2m()

            RaceRegistration.objects.get_or_create(
                participant=reg,
                event=event,
                race=race,
            )

            from .email_utils import send_registration_confirmation
            send_registration_confirmation(reg, request)

            messages.success(
                request,
                f"Registration for {race.name} — {event.title} submitted!",
            )

            return redirect(
                reverse("accounts:registration_success")
                + f"?reg_id={reg.registration_id}"
            )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PublicRegistrationForm()

    states = DimState.objects.all().order_by("name")

    return render(
        request,
        "accounts/register_race_event.html",
        {
            "form": form,
            "states": states,
            "race": race,
            "event": event,
        },
    )

def register_race_by_type(request, race_uuid, event_type_id):
    """
    Public, race+event-type-scoped registration page:
    /register/race/<uuid>/type/<event_type_id>/

    Shows a picker of only this race's events whose category belongs to
    the given DimEventType (e.g. only Road Cycling events, not Track).
    The chosen event is validated server-side on POST to make sure it
    really belongs to this race and this event type (anti-tampering) -
    never trusted purely from the picker's submitted value.
    """
    race = get_object_or_404(Race, uuid=race_uuid)

    available_events = Event.objects.filter(
        race=race,
        category__event_type_id=event_type_id,
    ).select_related("category", "category__event_type")

    if request.method == "POST":
        event_id = request.POST.get("event_id")

        event = get_object_or_404(
            Event.objects.select_related("race"),
            id=event_id,
            race=race,
            category__event_type_id=event_type_id,
        )

        form = PublicRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            reg = form.save(commit=False)
            reg.registration_type = "race"
            reg.race = race
            reg.save()
            form.save_m2m()

            RaceRegistration.objects.get_or_create(
                participant=reg,
                event=event,
                race=race,
            )

            from .email_utils import send_registration_confirmation
            send_registration_confirmation(reg, request)

            messages.success(
                request,
                f"Registration for {race.name} — {event.title} submitted!",
            )

            return redirect(
                reverse("accounts:registration_success")
                + f"?reg_id={reg.registration_id}"
            )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PublicRegistrationForm()

    states = DimState.objects.all().order_by("name")

    return render(
        request,
        "accounts/register_race_by_type.html",
        {
            "form": form,
            "states": states,
            "race": race,
            "available_events": available_events,
        },
    )

def register_tournament_category(request, category_uuid):
    """
    Public, single-category registration page:
    /register/tournament-category/<uuid>/

    Which category a participant enters is determined ONLY by
    category_uuid from the URL - never from posted form data. No
    tournament picker, no category checkboxes: the category is fixed
    by the link. Partner slots (for doubles/team formats) still work
    exactly as before.
    """
    tournament_category = get_object_or_404(
        TournamentCategory.objects.select_related(
            "entry_format", "category", "tournament"
        ),
        uuid=category_uuid,
        is_active=True,
        registration_open=True,
    )

    max_players = tournament_category.entry_format.maximum_players
    partner_positions = list(range(2, max_players + 1))

    if request.method == "POST":
        form = PublicRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            reg = form.save(commit=False)
            reg.registration_type = "tournament"
            reg.race = None
            reg.save()
            form.save_m2m()

            try:
                confirmed_status = EntryStatus.objects.get(code="confirmed", is_active=True)
                waitlisted_status = EntryStatus.objects.get(code="waitlisted", is_active=True)
            except EntryStatus.DoesNotExist:
                messages.error(
                    request,
                    "Tournament registration is temporarily unavailable because "
                    "Confirmed or Waitlisted status is missing. Please contact the organizers.",
                )
                return redirect(request.path)

            registrant_user = get_or_create_user_for_registration(reg.name, reg.email)
            if registrant_user is None:
                messages.error(request, "An email address is required for tournament registration.")
                return redirect(request.path)

            maximum_entries = tournament_category.maximum_entries
            confirmed_entry_count = tournament_category.entries.filter(
                status__code__iexact="confirmed"
            ).count()

            selected_status = (
                waitlisted_status
                if maximum_entries and confirmed_entry_count >= maximum_entries
                else confirmed_status
            )

            entry = TournamentEntry.objects.create(
                tournament_category=tournament_category,
                registration=reg,
                status=selected_status,
                display_name=reg.name if max_players == 1 else "",
                created_by=registrant_user,
            )

            TournamentEntryPlayer.objects.create(
                entry=entry,
                player=registrant_user,
                position=1,
                is_captain=True,
            )

            for position in partner_positions:
                field_prefix = f"{tournament_category.id}_{position}"

                partner_email = request.POST.get(f"partner_email_{field_prefix}", "").strip()
                partner_name = request.POST.get(f"partner_name_{field_prefix}", "").strip()
                manual_email = request.POST.get(f"partner_email_manual_{field_prefix}", "").strip()
                manual_name = request.POST.get(f"partner_name_manual_{field_prefix}", "").strip()

                final_email = partner_email or manual_email
                final_name = partner_name or manual_name

                if not final_email:
                    continue

                partner_reg, _ = Registration.objects.get_or_create(
                    email=final_email,
                    registration_type="tournament",
                    defaults={"name": final_name or final_email},
                )

                partner_user = get_or_create_user_for_registration(partner_reg.name, partner_reg.email)
                if partner_user is None:
                    continue

                TournamentEntryPlayer.objects.get_or_create(
                    entry=entry,
                    player=partner_user,
                    defaults={"position": position, "is_captain": False},
                )

            from .email_utils import send_registration_confirmation
            send_registration_confirmation(reg, request)

            messages.success(
                request,
                f"Entry submitted for {tournament_category} ({selected_status.name}).",
            )

            return redirect(
                reverse("accounts:registration_success")
                + f"?reg_id={reg.registration_id}"
            )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PublicRegistrationForm()

    states = DimState.objects.all().order_by("name")

    return render(
        request,
        "accounts/register_tournament_category.html",
        {
            "form": form,
            "states": states,
            "tournament_category": tournament_category,
            "partner_positions": partner_positions,
        },
    )

def register_tournament(request, tournament_uuid):
    """
    Public, tournament-scoped registration page:
    /register/tournament/<uuid>/

    Shows a picker of this tournament's own open categories only. The
    chosen category is validated server-side on POST to make sure it
    really belongs to this tournament (anti-tampering) - never trusted
    purely from the picker's submitted value. Partner slots (for
    doubles/team formats) are computed per-category once the category
    is known, same as register_tournament_category.
    """
    tournament = get_object_or_404(Tournament, uuid=tournament_uuid)

    available_categories = TournamentCategory.objects.filter(
        tournament=tournament,
        is_active=True,
        registration_open=True,
    ).select_related("entry_format", "category")

    if request.method == "POST":
        category_id = request.POST.get("tournament_category_id")

        tournament_category = get_object_or_404(
            TournamentCategory.objects.select_related(
                "entry_format", "category", "tournament"
            ),
            id=category_id,
            tournament=tournament,
            is_active=True,
            registration_open=True,
        )

        max_players = tournament_category.entry_format.maximum_players
        partner_positions = list(range(2, max_players + 1))

        form = PublicRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            reg = form.save(commit=False)
            reg.registration_type = "tournament"
            reg.race = None
            reg.save()
            form.save_m2m()

            try:
                confirmed_status = EntryStatus.objects.get(code="confirmed", is_active=True)
                waitlisted_status = EntryStatus.objects.get(code="waitlisted", is_active=True)
            except EntryStatus.DoesNotExist:
                messages.error(
                    request,
                    "Tournament registration is temporarily unavailable because "
                    "Confirmed or Waitlisted status is missing. Please contact the organizers.",
                )
                return redirect(request.path)

            registrant_user = get_or_create_user_for_registration(reg.name, reg.email)
            if registrant_user is None:
                messages.error(request, "An email address is required for tournament registration.")
                return redirect(request.path)

            maximum_entries = tournament_category.maximum_entries
            confirmed_entry_count = tournament_category.entries.filter(
                status__code__iexact="confirmed"
            ).count()

            selected_status = (
                waitlisted_status
                if maximum_entries and confirmed_entry_count >= maximum_entries
                else confirmed_status
            )

            entry = TournamentEntry.objects.create(
                tournament_category=tournament_category,
                registration=reg,
                status=selected_status,
                display_name=reg.name if max_players == 1 else "",
                created_by=registrant_user,
            )

            TournamentEntryPlayer.objects.create(
                entry=entry,
                player=registrant_user,
                position=1,
                is_captain=True,
            )

            for position in partner_positions:
                field_prefix = f"{tournament_category.id}_{position}"

                partner_email = request.POST.get(f"partner_email_{field_prefix}", "").strip()
                partner_name = request.POST.get(f"partner_name_{field_prefix}", "").strip()
                manual_email = request.POST.get(f"partner_email_manual_{field_prefix}", "").strip()
                manual_name = request.POST.get(f"partner_name_manual_{field_prefix}", "").strip()

                final_email = partner_email or manual_email
                final_name = partner_name or manual_name

                if not final_email:
                    continue

                partner_reg, _ = Registration.objects.get_or_create(
                    email=final_email,
                    registration_type="tournament",
                    defaults={"name": final_name or final_email},
                )

                partner_user = get_or_create_user_for_registration(partner_reg.name, partner_reg.email)
                if partner_user is None:
                    continue

                TournamentEntryPlayer.objects.get_or_create(
                    entry=entry,
                    player=partner_user,
                    defaults={"position": position, "is_captain": False},
                )

            from .email_utils import send_registration_confirmation
            send_registration_confirmation(reg, request)

            messages.success(
                request,
                f"Entry submitted for {tournament_category} ({selected_status.name}).",
            )

            return redirect(
                reverse("accounts:registration_success")
                + f"?reg_id={reg.registration_id}"
            )
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PublicRegistrationForm()

    states = DimState.objects.all().order_by("name")

    return render(
        request,
        "accounts/register_tournament.html",
        {
            "form": form,
            "states": states,
            "tournament": tournament,
            "available_categories": available_categories,
        },
    )


@require_GET
def ajax_load_districts(request):
    state_id = request.GET.get('state_id') or request.GET.get('state')
    if not state_id:
        return JsonResponse({'error': 'state_id required'}, status=400)
    districts = DimDistrict.objects.filter(state_id=state_id).order_by('name')
    result = [{'id': d.id, 'name': d.name} for d in districts]
    return JsonResponse({'districts': result})


@require_GET
def ajax_tournament_categories(request):
    """
    Mirrors ajax_load_districts: given a tournament, return its active,
    registration-open categories for the Section-3 Tournament panel.
    """
    tournament_id = request.GET.get('tournament_id')
    if not tournament_id:
        return JsonResponse({'error': 'tournament_id required'}, status=400)

    categories = TournamentCategory.objects.filter(
        tournament_id=tournament_id,
        is_active=True,
        registration_open=True,
    ).select_related('category', 'entry_format')

    result = [
        {
            'id': c.id,
            'name': c.category.name,
            'entry_format': c.entry_format.name,
            'min_players': c.entry_format.minimum_players,
            'max_players': c.entry_format.maximum_players,
            'entry_fee': str(c.entry_fee),
        }
        for c in categories
    ]
    return JsonResponse({'categories': result})


@require_GET
def ajax_partner_search(request):
    """
    Lets a user find a partner who has already filled the public form
    (registration_type='tournament'), so their details autofill instead
    of being retyped. Purely a lookup — does not create anything.
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    matches = Registration.objects.filter(
        registration_type='tournament'
    ).filter(
        Q(name__icontains=q) | Q(email__icontains=q)
    ).exclude(email='').exclude(email__isnull=True).distinct()[:10]

    result = [{'id': r.id, 'name': r.name, 'email': r.email} for r in matches]
    return JsonResponse({'results': result})


@login_required
def profile(request):
    user = request.user
    registrations = Registration.objects.filter(email=user.email).prefetch_related(
        'tournament_entries__tournament_category__tournament',
        'tournament_entries__tournament_category__category',
        'tournament_entries__status',
    ).order_by('-created_at')
    return render(request, 'accounts/profile.html', {'registrations': registrations, 'user': user})


@login_required
def registration_edit(request, pk):
    reg = get_object_or_404(Registration, pk=pk)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES, instance=reg)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration updated successfully.")
            return redirect(reverse('accounts:profile'))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm(instance=reg)
    return render(request, 'accounts/registration_edit.html', {'form': form, 'reg': reg})


def viewLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('accounts:check_profile')
        messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')


def registration_success(request):
    reg_id = request.GET.get('reg_id')
    registration = None

    if reg_id:
        registration = get_object_or_404(
            Registration.objects.prefetch_related(
                'tournament_entries__tournament_category__tournament',
                'tournament_entries__tournament_category__category',
                'tournament_entries__tournament_category__entry_format',
                'tournament_entries__status',
            ),
            registration_id=reg_id
        )

    return render(request, 'accounts/registration_success.html', {
        'registration': registration
    })


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    registrations = Registration.objects.filter(
        email=request.user.email
    ).select_related('race').prefetch_related(
        'tournament_entries__tournament_category__tournament',
        'tournament_entries__tournament_category__category',
        'tournament_entries__status',
    ).order_by('-created_at')

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'registrations': registrations
    })


@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile_instance = form.save()

            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            messages.success(request, "Athlete profile updated!")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def view_registration_details(request, reg_id):
    """
    Shows the details of a specific registration based on the CTCC-0001 ID.
    """
    registration = get_object_or_404(Registration, registration_id=reg_id)

    return render(request, 'accounts/registration_detail.html', {
        'registration': registration
    })