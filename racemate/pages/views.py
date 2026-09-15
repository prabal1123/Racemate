

# # app_pages/views.py
# from django.shortcuts import render
# from django.urls import reverse
# from django.utils.safestring import mark_safe

# def home(request):
#     """
#     Homepage: Welcome hero + Quick Links only (no recent registrations).
#     SVG strings kept inline.
#     """
#     svg_file_edit = '''
#     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-6 w-6" aria-hidden="true">
#       <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5M16 3l5 5M12 7l5 5" />
#     </svg>
#     '''
#     svg_login = '''
#     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-6 w-6" aria-hidden="true">
#       <path stroke-linecap="round" stroke-linejoin="round" d="M15 12H3m12 0l-4-4m4 4l-4 4M21 12v6a2 2 0 0 1-2 2H9" />
#     </svg>
#     '''
#     svg_user_plus = '''
#     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-6 w-6" aria-hidden="true">
#       <path stroke-linecap="round" stroke-linejoin="round" d="M15 14a4 4 0 1 0-6 0M12 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM19 9v6M22 12h-6" />
#     </svg>
#     '''
#     svg_arrow = '''
#     <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-5 w-5" aria-hidden="true">
#       <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
#     </svg>
#     '''

#     # Prefer reverse(); fallback to static paths when names are missing
#     try:
#         register_href = reverse("accounts:register")
#     except Exception:
#         register_href = "/register/"

#     try:
#         login_href = reverse("account_login")
#     except Exception:
#         login_href = "/accounts/login/"

#     try:
#         signup_href = reverse("account_signup")
#     except Exception:
#         signup_href = "/accounts/signup/"

#     quick_links = [
#         {
#             "icon": mark_safe(svg_file_edit),
#             "title": "Register",
#             "description": "Register for upcoming events",
#             "href": register_href,
#         },
#         {
#             "icon": mark_safe(svg_login),
#             "title": "Account Login",
#             "description": "Sign in to your account",
#             "href": login_href,
#         },
#         {
#             "icon": mark_safe(svg_user_plus),
#             "title": "Sign up",
#             "description": "Create a new account",
#             "href": signup_href,
#         },
#     ]

#     context = {
#         "quick_links": quick_links,
#         "arrow_icon": mark_safe(svg_arrow),
#         # add other homepage context (hero, announcements) as needed
#     }
#     return render(request, "accounts/home.html", context)


# app_pages/views.py
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from app_races.models import Race
from app_tournaments.models import Tournament


def _build_events(races, tournaments):
    """
    Normalizes Race (cycling/BMX) and Tournament (badminton/pickleball)
    objects into one flat list of plain dicts the template can loop
    over without caring which model each item came from.
    """
    events = []

    for race in races:
        events.append({
            "kind": "race",
            "id": race.id,
            "name": race.name,
            # Race has no sport field yet — every Race is treated as
            # cycling for now. If you later want BMX split out, either
            # add a `sport` FK to Race (mirroring Tournament.sport) or
            # infer it from Event.category.
            "sport": "cycling",
            "status": race.status,
            "start": race.race_start,
            "location": race.location,
            "participant_count": race.race_registrations.count(),
            "categories": [
                {
                    "label": e.title,
                    "suffix": f"{e.distance_km}km" if e.distance_km else "",
                }
                for e in race.events.all()
            ],
            "register_query": f"race_id={race.id}",
            "winners": [],
        })

    for tournament in tournaments:
        sport_name = tournament.sport.name.lower()

        categories = []
        winners = []
        participant_count = 0

        for cat in tournament.categories.all():
            participant_count += cat.entries.count()
            categories.append({
                "label": cat.category.name,
                "suffix": cat.entry_format.name if cat.entry_format else "",
            })

            champion = cat.get_champion()
            if champion:
                winners.append(
                    f"{cat.category.name}: {champion.get_display_name()}"
                )

        events.append({
            "kind": "tournament",
            "id": tournament.id,
            "name": tournament.name,
            "sport": sport_name,
            "status": tournament.status,
            "start": tournament.tournament_start,
            "location": tournament.venue,
            "participant_count": participant_count,
            "categories": categories,
            # TODO: point this at your actual tournament entry flow —
            # this assumes a tournament_id query param the way race_id
            # is used today. Adjust the url name/param if different.
            "register_query": f"tournament_id={tournament.id}",
            "winners": winners,
        })

    events.sort(key=lambda e: e["start"])
    return events


def home(request):
    """
    Homepage: Welcome hero + Quick Links + multi-sport upcoming/past events.
    SVG strings kept inline.
    """
    svg_file_edit = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-6 w-6" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5M16 3l5 5M12 7l5 5" />
    </svg>
    '''
    svg_login = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-6 w-6" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" d="M15 12H3m12 0l-4-4m4 4l-4 4M21 12v6a2 2 0 0 1-2 2H9" />
    </svg>
    '''
    svg_user_plus = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-6 w-6" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" d="M15 14a4 4 0 1 0-6 0M12 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM19 9v6M22 12h-6" />
    </svg>
    '''
    svg_arrow = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-5 w-5" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
    </svg>
    '''

    # Prefer reverse(); fallback to static paths when names are missing
    try:
        register_href = reverse("accounts:register")
    except Exception:
        register_href = "/register/"

    try:
        login_href = reverse("account_login")
    except Exception:
        login_href = "/accounts/login/"

    try:
        signup_href = reverse("account_signup")
    except Exception:
        signup_href = "/accounts/signup/"

    quick_links = [
        {
            "icon": mark_safe(svg_file_edit),
            "title": "Register",
            "description": "Register for upcoming events",
            "href": register_href,
        },
        {
            "icon": mark_safe(svg_login),
            "title": "Account Login",
            "description": "Sign in to your account",
            "href": login_href,
        },
        {
            "icon": mark_safe(svg_user_plus),
            "title": "Sign up",
            "description": "Create a new account",
            "href": signup_href,
        },
    ]

    # ── Multi-sport events (cycling/BMX races + badminton/pickleball tournaments) ──
    now = timezone.now()

    races = Race.objects.prefetch_related("events", "race_registrations")

    tournaments = Tournament.objects.select_related("sport").prefetch_related(
        "categories__category",
        "categories__entry_format",
        "categories__entries",
        "categories__rounds__matches__winner__players__player",
    )

    events = _build_events(races, tournaments)

    upcoming_events = [
        e for e in events
        if e["status"] in ("LIVE NOW", "REGISTRATION OPEN") or e["start"] >= now
    ]
    past_events = [
        e for e in events
        if e["status"] not in ("LIVE NOW", "REGISTRATION OPEN") and e["start"] < now
    ]

    context = {
        "quick_links": quick_links,
        "arrow_icon": mark_safe(svg_arrow),
        "upcoming_events": upcoming_events,
        "past_events": past_events,
        "now": now,
        # add other homepage context (announcements) as needed
    }
    return render(request, "accounts/home.html", context)