

# from .forms import UserProfileForm
# # accounts/views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.urls import reverse
# from django.http import JsonResponse
# from django.views.decorators.http import require_GET
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import authenticate, login
# from django.utils.safestring import mark_safe
# from app_races.models import Race, Event, RaceRegistration
# from django.contrib.auth.models import User
# from django import forms

# from .models import Registration
# from .forms import RegistrationForm
# from app_admin.models import DimDistrict, DimState
# from django.shortcuts import render
# from .models import Profile
# from app_races.models import Race
# from django.utils import timezone

# def home(request):
#     """
#     Homepage: Real Race Data + Hero + Results
#     """
#     # --- SVG ICONS (Kept as is) ---
#     svg_register = '''<svg>...</svg>'''
#     svg_login = '''<svg>...</svg>'''
    
#     # --- FETCH REAL DATA ---
#     # We fetch all races ordered by the start date
#     # .prefetch_related('registrations') makes the rider count query much faster
#     # db_races = Race.objects.all().prefetch_related('registrations').order_by('race_start')
#     # Use 'race_registrations' (plural) as defined in your updated RaceRegistration model
#     # db_races = Race.objects.all().prefetch_related('race_registrations').order_by('race_start')

#     now = timezone.now() 
#     db_races = Race.objects.all().prefetch_related('race_registrations', 'events').order_by('race_start')

#     # --- DUMMY RESULTS (Keep until you create a Results model) ---
#     recent_results = [
#         {"event": "Table Mountain Time Trial", "date": "Feb 28, 2026", "results": [{"name": "Liam Jacobs", "time": "2h 14m 32s"}, {"name": "Thabo Molefe", "time": "2h 16m 08s"}, {"name": "Sarah van Niekerk", "time": "2h 18m 45s"}]},
#         {"event": "Winelands Classic", "date": "Feb 15, 2026", "results": [{"name": "Nina Botha", "time": "3h 02m 11s"}, {"name": "Chris Dlamini", "time": "3h 04m 50s"}, {"name": "James Le Roux", "time": "3h 07m 22s"}]},
#         {"event": "Midlands Meander MTB", "date": "Jan 25, 2026", "results": [{"name": "Ethan Pretorius", "time": "4h 31m 09s"}, {"name": "Zanele Nkosi", "time": "4h 35m 44s"}, {"name": "Pieter du Toit", "time": "4h 38m 01s"}]},
#     ]

#     context = {
#         "races": db_races,  # Passing the real QuerySet now
#         "recent_results": recent_results,
#         "now": now, # Pass current time to template for status logic
#     }
#     return render(request, "accounts/home.html", context)


# # --- NEW TRAFFIC CONTROLLER ---
# @login_required
# def check_profile_completion(request):
#     """
#     Traffic controller: 
#     Checks both User and Profile models, then sends the user to the right place.
#     """
#     user = request.user
    
#     # 1. Get or create the profile (Safety check)
#     profile, created = Profile.objects.get_or_create(user=user)

#     # 2. Check for missing mandatory info
#     # We check the User model AND the Profile model phone number
#     if not user.first_name or not user.last_name or not profile.phone_number:
#         messages.info(request, "Almost there! Please complete your profile details.")
#         return redirect('accounts:profile_edit') 

#     # 3. If everything is complete, send them to their new Profile Page
#     return redirect('accounts:profile')# --- REMAINING VIEWS ---



# def register(request):
#     """
#     Handles race registration for multiple events while maintaining
#     a single Bib/Registration ID. Sends confirmation email on success.
#     """
#     now = timezone.now()
#     active_races = Race.objects.filter(
#         registration_start__lte=now,
#         race_start__gte=now.date()
#     ).prefetch_related('events')

#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
#         selected_event_ids = request.POST.getlist('selected_events')

#         if not selected_event_ids:
#             messages.error(request, "Please select at least one event category.")
#             states = DimState.objects.all().order_by('name')
#             return render(request, 'accounts/register.html', {
#                 'form': form,
#                 'states': states,
#                 'active_races': active_races
#             })

#         if form.is_valid():
#             reg = form.save(commit=False)

#             try:
#                 first_event = Event.objects.get(id=selected_event_ids[0])
#                 reg.race = first_event.race
#                 reg.save()
#                 form.save_m2m()

#                 for event_id in selected_event_ids:
#                     event_obj = Event.objects.get(id=event_id)
#                     RaceRegistration.objects.get_or_create(
#                         participant=reg,
#                         event=event_obj,
#                         race=event_obj.race
#                     )

#                 # Send confirmation email
#                 from .email_utils import send_registration_confirmation
#                 send_registration_confirmation(reg, request)

#                 messages.success(request, f"Registration for {reg.race.name} submitted!")
#                 return redirect(reverse('accounts:registration_success') + f'?reg_id={reg.registration_id}')

#             except Event.DoesNotExist:
#                 messages.error(request, "One of the selected events is invalid.")
#                 return redirect('accounts:register')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = RegistrationForm()

#     preselected_race_id = request.GET.get('race_id')
#     states = DimState.objects.all().order_by('name')

#     return render(request, 'accounts/register.html', {
#         'form': form,
#         'states': states,
#         'active_races': active_races,
#         'preselected_race_id': preselected_race_id
#     })

# @require_GET
# def ajax_load_districts(request):
#     state_id = request.GET.get('state_id') or request.GET.get('state')
#     if not state_id: return JsonResponse({'error': 'state_id required'}, status=400)
#     districts = DimDistrict.objects.filter(state_id=state_id).order_by('name')
#     result = [{'id': d.id, 'name': d.name} for d in districts]
#     return JsonResponse({'districts': result})

# @login_required
# def profile(request):
#     user = request.user
#     registrations = Registration.objects.filter(email=user.email).order_by('-created_at')
#     return render(request, 'accounts/profile.html', {'registrations': registrations, 'user': user})

# @login_required
# def registration_edit(request, pk):
#     reg = get_object_or_404(Registration, pk=pk)
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES, instance=reg)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Registration updated successfully.")
#             return redirect(reverse('accounts:profile'))
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = RegistrationForm(instance=reg)
#     return render(request, 'accounts/registration_edit.html', {'form': form, 'reg': reg})

# def viewLogin(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user:
#             login(request, user)
#             return redirect('accounts:check_profile')
#         messages.error(request, 'Invalid username or password')
#     return render(request, 'accounts/login.html')

# # def registration_success(request):
# #     return render(request, 'accounts/registration_success.html')

# def registration_success(request):
#     # Get the ID from the URL query parameters
#     reg_id = request.GET.get('reg_id')
#     registration = None
    
#     if reg_id:
#         # Fetch the specific registration using the new registration_id field
#         registration = get_object_or_404(Registration, registration_id=reg_id)
        
#     return render(request, 'accounts/registration_success.html', {
#         'registration': registration
#     })


# # @login_required
# # def profile_view(request):
# #     # This prevents the "RelatedObjectDoesNotExist" error by creating the row if missing
# #     profile, created = Profile.objects.get_or_create(user=request.user)
# #     return render(request, 'accounts/profile.html', {'profile': profile})

# @login_required
# def profile_view(request):
#     profile, created = Profile.objects.get_or_create(user=request.user)
    
#     # Fetch all registrations linked to this user's email
#     # Using .select_related('race') makes the race name load instantly
#     registrations = Registration.objects.filter(email=request.user.email).select_related('race').order_by('-created_at')
    
#     return render(request, 'accounts/profile.html', {
#         'profile': profile,
#         'registrations': registrations
#     })


# @login_required
# def profile_edit(request):
#     # Ensure profile exists for this user
#     profile, created = Profile.objects.get_or_create(user=request.user)
    
#     if request.method == 'POST':
#         # request.FILES is required for the Profile Image to work
#         form = UserProfileForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             # 1. Save Profile fields (phone, bio, pan, etc.)
#             profile_instance = form.save()
            
#             # 2. Update the User model fields (first_name, last_name)
#             user = request.user
#             user.first_name = form.cleaned_data['first_name']
#             user.last_name = form.cleaned_data['last_name']
#             user.save()
            
#             messages.success(request, "Athlete profile updated!")
#             return redirect('accounts:profile')
#     else:
#         form = UserProfileForm(instance=profile)
    
#     return render(request, 'accounts/profile_edit.html', {'form': form})


# @login_required # Optional: remove if you want users to view it via a public link
# def view_registration_details(request, reg_id):

#     """
#     Shows the details of a specific registration based on the CTCC-0001 ID.
#     """
#     registration = get_object_or_404(Registration, registration_id=reg_id)
    
#     return render(request, 'accounts/registration_detail.html', {
#         'registration': registration
#     })


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
from .forms import RegistrationForm
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


def home(request):
    """
    Homepage: Real Race Data + Hero + Results
    """
    # --- SVG ICONS (Kept as is) ---
    svg_register = '''<svg>...</svg>'''
    svg_login = '''<svg>...</svg>'''

    now = timezone.now()
    db_races = Race.objects.all().prefetch_related('race_registrations', 'events').order_by('race_start')

    # --- DUMMY RESULTS (Keep until you create a Results model) ---
    recent_results = [
        {"event": "Table Mountain Time Trial", "date": "Feb 28, 2026", "results": [{"name": "Liam Jacobs", "time": "2h 14m 32s"}, {"name": "Thabo Molefe", "time": "2h 16m 08s"}, {"name": "Sarah van Niekerk", "time": "2h 18m 45s"}]},
        {"event": "Winelands Classic", "date": "Feb 15, 2026", "results": [{"name": "Nina Botha", "time": "3h 02m 11s"}, {"name": "Chris Dlamini", "time": "3h 04m 50s"}, {"name": "James Le Roux", "time": "3h 07m 22s"}]},
        {"event": "Midlands Meander MTB", "date": "Jan 25, 2026", "results": [{"name": "Ethan Pretorius", "time": "4h 31m 09s"}, {"name": "Zanele Nkosi", "time": "4h 35m 44s"}, {"name": "Pieter du Toit", "time": "4h 38m 01s"}]},
    ]

    context = {
        "races": db_races,
        "recent_results": recent_results,
        "now": now,
    }
    return render(request, "accounts/home.html", context)


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


# ============================================================
# REGISTER — handles BOTH race registration and tournament
# entry, branched by the `registration_type` field posted
# from the Section-3 toggle in register.html
# ============================================================
def register(request):
    """
    Handles both:

    1. Race registration
    2. Tournament enrollment

    Tournament flow:

    - User selects one or more tournament categories.
    - One TournamentEntry is automatically created
      for every selected category.
    - The registrant is automatically attached as player 1.
    - Partners are automatically attached for doubles/team events.
    - Entry is confirmed when capacity is available.
    - Entry is waitlisted when the category is full.
    """
    now = timezone.now()

    active_races = (
        Race.objects
        .filter(
            registration_start__lte=now,
            race_start__gte=now.date(),
        )
        .prefetch_related("events")
    )

    active_tournaments = (
        Tournament.objects
        .filter(
            registration_start__lte=now,
            registration_end__gte=now,
        )
        .prefetch_related(
            "categories__category",
            "categories__entry_format",
        )
    )

    _attach_partner_position_ranges(
        active_tournaments
    )

    if request.method == "POST":
        registration_type = request.POST.get(
            "registration_type",
            "race",
        )

        form = RegistrationForm(
            request.POST,
            request.FILES,
        )

        selected_event_ids = request.POST.getlist(
            "selected_events"
        )

        selected_category_ids = request.POST.getlist(
            "selected_tournament_categories"
        )

        # Race registration requires at least one race event.
        if (
            registration_type == "race"
            and not selected_event_ids
        ):
            messages.error(
                request,
                "Please select at least one event category.",
            )

            states = DimState.objects.all().order_by(
                "name"
            )

            return render(
                request,
                "accounts/register.html",
                {
                    "form": form,
                    "states": states,
                    "active_races": active_races,
                    "active_tournaments": (
                        active_tournaments
                    ),
                },
            )

        # Tournament registration requires at least
        # one tournament category.
        if (
            registration_type == "tournament"
            and not selected_category_ids
        ):
            messages.error(
                request,
                "Please select at least one "
                "tournament category.",
            )

            states = DimState.objects.all().order_by(
                "name"
            )

            return render(
                request,
                "accounts/register.html",
                {
                    "form": form,
                    "states": states,
                    "active_races": active_races,
                    "active_tournaments": (
                        active_tournaments
                    ),
                },
            )

        if form.is_valid():
            reg = form.save(commit=False)
            reg.registration_type = registration_type

            try:
                # ============================================
                # RACE REGISTRATION
                # ============================================
                if registration_type == "race":
                    first_event = Event.objects.get(
                        id=selected_event_ids[0]
                    )

                    reg.race = first_event.race
                    reg.save()

                    form.save_m2m()

                    for event_id in selected_event_ids:
                        event_obj = Event.objects.get(
                            id=event_id
                        )

                        RaceRegistration.objects.get_or_create(
                            participant=reg,
                            event=event_obj,
                            race=event_obj.race,
                        )

                    from .email_utils import (
                        send_registration_confirmation,
                    )

                    send_registration_confirmation(
                        reg,
                        request,
                    )

                    messages.success(
                        request,
                        (
                            f"Registration for "
                            f"{reg.race.name} submitted!"
                        ),
                    )

                    return redirect(
                        reverse(
                            "accounts:registration_success"
                        )
                        + f"?reg_id={reg.registration_id}"
                    )

                # ============================================
                # TOURNAMENT REGISTRATION
                # ============================================
                reg.race = None
                reg.save()

                form.save_m2m()

                # Required tournament entry statuses.
                try:
                    confirmed_status = (
                        EntryStatus.objects.get(
                            code="confirmed",
                            is_active=True,
                        )
                    )

                    waitlisted_status = (
                        EntryStatus.objects.get(
                            code="waitlisted",
                            is_active=True,
                        )
                    )

                except EntryStatus.DoesNotExist:
                    messages.error(
                        request,
                        (
                            "Tournament registration is "
                            "temporarily unavailable because "
                            "Confirmed or Waitlisted status "
                            "is missing. Please contact the "
                            "organizers."
                        ),
                    )

                    return redirect(
                        "accounts:register"
                    )

                # Create or resolve the registrant's user.
                # This user becomes player position 1.
                registrant_user = (
                    get_or_create_user_for_registration(
                        reg.name,
                        reg.email,
                    )
                )

                if registrant_user is None:
                    messages.error(
                        request,
                        (
                            "An email address is required "
                            "for tournament registration."
                        ),
                    )

                    return redirect(
                        "accounts:register"
                    )

                entries_created = []

                # Create one TournamentEntry for every
                # selected tournament category.
                for category_id in selected_category_ids:
                    tournament_category = (
                        TournamentCategory.objects
                        .filter(
                            id=category_id,
                            is_active=True,
                            registration_open=True,
                        )
                        .select_related(
                            "entry_format",
                            "category",
                            "tournament",
                        )
                        .first()
                    )

                    # Ignore stale or invalid category IDs.
                    if not tournament_category:
                        continue

                    entry_format = (
                        tournament_category.entry_format
                    )

                    maximum_entries = (
                        tournament_category
                        .maximum_entries
                    )

                    confirmed_entry_count = (
                        tournament_category.entries
                        .filter(
                            status__code__iexact=(
                                "confirmed"
                            )
                        )
                        .count()
                    )

                    # Capacity available:
                    # Confirm the entry.
                    #
                    # Capacity full:
                    # Add the entry to the waitlist.
                    if (
                        maximum_entries
                        and confirmed_entry_count
                        >= maximum_entries
                    ):
                        selected_status = (
                            waitlisted_status
                        )
                    else:
                        selected_status = (
                            confirmed_status
                        )

                    # Automatically create the entry under
                    # the category selected by the user.
                    entry = (
                        TournamentEntry.objects.create(
                            tournament_category=(
                                tournament_category
                            ),
                            registration=reg,
                            status=selected_status,
                            display_name=(
                                reg.name
                                if (
                                    entry_format
                                    .maximum_players
                                    == 1
                                )
                                else ""
                            ),
                            created_by=registrant_user,
                        )
                    )

                    # Automatically attach the registrant
                    # as player number 1 and captain.
                    TournamentEntryPlayer.objects.create(
                        entry=entry,
                        player=registrant_user,
                        position=1,
                        is_captain=True,
                    )

                    # Attach doubles/team partners.
                    max_players = (
                        entry_format.maximum_players
                    )

                    for position in range(
                        2,
                        max_players + 1,
                    ):
                        field_prefix = (
                            f"{category_id}_{position}"
                        )

                        partner_email = (
                            request.POST.get(
                                (
                                    "partner_email_"
                                    f"{field_prefix}"
                                ),
                                "",
                            )
                            .strip()
                        )

                        partner_name = (
                            request.POST.get(
                                (
                                    "partner_name_"
                                    f"{field_prefix}"
                                ),
                                "",
                            )
                            .strip()
                        )

                        manual_email = (
                            request.POST.get(
                                (
                                    "partner_email_manual_"
                                    f"{field_prefix}"
                                ),
                                "",
                            )
                            .strip()
                        )

                        manual_name = (
                            request.POST.get(
                                (
                                    "partner_name_manual_"
                                    f"{field_prefix}"
                                ),
                                "",
                            )
                            .strip()
                        )

                        final_email = (
                            partner_email
                            or manual_email
                        )

                        final_name = (
                            partner_name
                            or manual_name
                        )

                        # Optional team position left empty.
                        if not final_email:
                            continue

                        # Create a lightweight registration
                        # for the partner when required.
                        partner_reg, _ = (
                            Registration.objects
                            .get_or_create(
                                email=final_email,
                                registration_type=(
                                    "tournament"
                                ),
                                defaults={
                                    "name": (
                                        final_name
                                        or final_email
                                    )
                                },
                            )
                        )

                        partner_user = (
                            get_or_create_user_for_registration(
                                partner_reg.name,
                                partner_reg.email,
                            )
                        )

                        if partner_user is None:
                            continue

                        TournamentEntryPlayer.objects.get_or_create(
                            entry=entry,
                            player=partner_user,
                            defaults={
                                "position": position,
                                "is_captain": False,
                            },
                        )

                    entries_created.append(
                        (
                            f"{tournament_category} "
                            f"({selected_status.name})"
                        )
                    )

                if not entries_created:
                    messages.error(
                        request,
                        (
                            "None of the selected tournament "
                            "categories were valid or open "
                            "for registration."
                        ),
                    )

                    return redirect(
                        "accounts:register"
                    )

                from .email_utils import (
                    send_registration_confirmation,
                )

                send_registration_confirmation(
                    reg,
                    request,
                )

                messages.success(
                    request,
                    (
                        "Tournament entries submitted for: "
                        f"{', '.join(entries_created)}."
                    ),
                )

                return redirect(
                    reverse(
                        "accounts:registration_success"
                    )
                    + f"?reg_id={reg.registration_id}"
                )

            except Event.DoesNotExist:
                messages.error(
                    request,
                    (
                        "One of the selected events "
                        "is invalid."
                    ),
                )

                return redirect(
                    "accounts:register"
                )

        else:
            messages.error(
                request,
                "Please correct the errors below.",
            )

    else:
        form = RegistrationForm()

    preselected_race_id = request.GET.get(
        "race_id"
    )

    states = DimState.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
            "states": states,
            "active_races": active_races,
            "active_tournaments": (
                active_tournaments
            ),
            "preselected_race_id": (
                preselected_race_id
            ),
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