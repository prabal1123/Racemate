# # accounts/views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.urls import reverse
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.http import JsonResponse, HttpResponseBadRequest
# from django.views.decorators.http import require_GET, require_POST

# from .models import Registration
# from .forms import RegistrationForm
# from django.utils.safestring import mark_safe

# from app_admin.models import DimDistrict, DimState  # used for ajax districts

# # def home(request):
# #     """
# #     Homepage: Welcome hero + Quick Links only (no recent registrations).
# #     """
# #     # inline SVG icons (explicit width/height so they stay small)
# #     svg_file_edit = '''
# #     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-6 w-6" aria-hidden="true">
# #       <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5M16 3l5 5M12 7l5 5" />
# #     </svg>
# #     '''
# #     svg_login = '''
# #     <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
# #         <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
# #         <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
# #     </svg>
# #     '''
# #     svg_user_plus = '''
# #     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-6 w-6" aria-hidden="true">
# #       <path stroke-linecap="round" stroke-linejoin="round" d="M15 14a4 4 0 1 0-6 0M12 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM19 9v6M22 12h-6" />
# #     </svg>
# #     '''
# #     svg_arrow = '''
# #     <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-5 w-5" aria-hidden="true">
# #       <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
# #     </svg>
# #     '''

# #     # Use reverse() when possible — fallback to path if URL name not present
# #     try:
# #         register_href = reverse("accounts:register")
# #     except Exception:
# #         register_href = "/register/"

# #     try:
# #         login_href = reverse("login")
# #     except Exception:
# #         login_href = "/accounts/login/"

# #     try:
# #         signup_href = reverse("account_signup")
# #     except Exception:
# #         signup_href = "/accounts/signup/"

# #     # Quick links data
# #     quick_links = [
# #         {
# #             "icon": mark_safe(svg_file_edit),
# #             "title": "Register",
# #             "description": "Register for upcoming events",
# #             "href": register_href,
# #         },
# #         {
# #             "icon": mark_safe(svg_login),
# #             "title": "Account Login",
# #             "description": "Sign in to your account",
# #             "href": login_href,
# #         },
# #         {
# #             "icon": mark_safe(svg_user_plus),
# #             "title": "Sign up",
# #             "description": "Create a new account",
# #             "href": signup_href,
# #         },
# #     ]

# #     context = {
# #         "quick_links": quick_links,
# #         "arrow_icon": mark_safe(svg_arrow),
# #         # No latest_regs provided on purpose — we are removing Recent Registrations
# #     }
# #     return render(request, "accounts/home.html", context)

# from django.shortcuts import render
# from django.urls import reverse
# from django.utils.safestring import mark_safe


# def home(request):
#     """
#     Homepage: Hero + Registration/Login Quick Links + Upcoming Races
#     """

#     # ------------------------
#     # SVG ICONS
#     # ------------------------

#     svg_register = '''
#     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
#          viewBox="0 0 24 24" fill="none" stroke="currentColor"
#          stroke-width="1.5" aria-hidden="true">
#       <path stroke-linecap="round" stroke-linejoin="round"
#             d="M11 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5M16 3l5 5M12 7l5 5" />
#     </svg>
#     '''

#     svg_login = '''
#     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
#          viewBox="0 0 24 24" fill="none" stroke="currentColor"
#          stroke-width="1.5" aria-hidden="true">
#       <path stroke-linecap="round" stroke-linejoin="round"
#             d="M15 12H3m0 0l4-4m-4 4l4 4m6-12h5a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-5" />
#     </svg>
#     '''

#     # ------------------------
#     # URL RESOLUTION
#     # ------------------------

#     try:
#         register_href = reverse("accounts:register")
#     except Exception:
#         register_href = "/register/"

#     try:
#         login_href = reverse("login")
#     except Exception:
#         login_href = "/accounts/login/"

#     # ------------------------
#     # QUICK LINKS (Only 2)
#     # ------------------------

#     quick_links = [
#         {
#             "icon": mark_safe(svg_register),
#             "title": "Register",
#             "description": "Register for upcoming cycling events",
#             "href": register_href,
#         },
#         {
#             "icon": mark_safe(svg_login),
#             "title": "Account Login",
#             "description": "Sign in to manage your registrations",
#             "href": login_href,
#         },
#     ]

#     # ------------------------
#     # DUMMY RACE DATA
#     # ------------------------

#     races = [
#         {
#             "name": "Cape Town Cycle Challenge",
#             "date": "Mar 15, 2026",
#             "location": "Cape Town, South Africa",
#             "riders": 2340,
#             "distance": 109,
#             "status": "live",  # live / open / soon
#         },
#         {
#             "name": "Stellenbosch Gran Fondo",
#             "date": "Apr 5, 2026",
#             "location": "Stellenbosch, South Africa",
#             "riders": 860,
#             "distance": 82,
#             "status": "open",
#         },
#         {
#             "name": "Karoo Desert Dash",
#             "date": "Apr 22, 2026",
#             "location": "Graaff-Reinet, South Africa",
#             "riders": 420,
#             "distance": 145,
#             "status": "open",
#         },
#         {
#             "name": "Garden Route Classic",
#             "date": "May 10, 2026",
#             "location": "Knysna, South Africa",
#             "riders": 0,
#             "distance": 120,
#             "status": "soon",
#         },
#         {
#             "name": "Durban Coastal Sprint",
#             "date": "Jun 1, 2026",
#             "location": "Durban, South Africa",
#             "riders": 0,
#             "distance": 65,
#             "status": "soon",
#         },
#         {
#             "name": "Joburg Urban Crit",
#             "date": "Jun 20, 2026",
#             "location": "Johannesburg, South Africa",
#             "riders": 0,
#             "distance": 40,
#             "status": "soon",
#         },
#     ]
#     recent_results = [
#     {
#         "event": "Table Mountain Time Trial",
#         "date": "Feb 28, 2026",
#         "results": [
#             {"name": "Liam Jacobs", "time": "2h 14m 32s"},
#             {"name": "Thabo Molefe", "time": "2h 16m 08s"},
#             {"name": "Sarah van Niekerk", "time": "2h 18m 45s"},
#         ],
#     },
#     {
#         "event": "Winelands Classic",
#         "date": "Feb 15, 2026",
#         "results": [
#             {"name": "Nina Botha", "time": "3h 02m 11s"},
#             {"name": "Chris Dlamini", "time": "3h 04m 50s"},
#             {"name": "James Le Roux", "time": "3h 07m 22s"},
#         ],
#     },
#     {
#         "event": "Midlands Meander MTB",
#         "date": "Jan 25, 2026",
#         "results": [
#             {"name": "Ethan Pretorius", "time": "4h 31m 09s"},
#             {"name": "Zanele Nkosi", "time": "4h 35m 44s"},
#             {"name": "Pieter du Toit", "time": "4h 38m 01s"},
#         ],
#     },
# ]

#     # ------------------------
#     # CONTEXT
#     # ------------------------

#     context = {
#         "races": races,
#         "recent_results": recent_results,
#     }

#     return render(request, "accounts/home.html", context)

# def register(request):
#     """
#     Public registration form endpoint (basic example).
#     Adjust fields and logic to suit your RegistrationForm.
#     """
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             reg = form.save(commit=False)
#             # perform any pre-save tweaks here (e.g., default category)
#             reg.save()
#             form.save_m2m()
#             messages.success(request, "Registration submitted. Thank you!")
#             # return redirect(reverse('accounts:home'))
#             return redirect('accounts:registration_success')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = RegistrationForm()

#     # supply states for the state select if your form template expects it
#     states = DimState.objects.all().order_by('name')
#     return render(request, 'accounts/register.html', {
#         'form': form,
#         'states': states,
#     })


# @require_GET
# def ajax_load_districts(request):
#     """
#     AJAX endpoint: given ?state_id=XX returns JSON list of districts.
#     Returns: [{'id': id, 'name': name}, ...]
#     """
#     state_id = request.GET.get('state_id') or request.GET.get('state')
#     if not state_id:
#         return JsonResponse({'error': 'state_id required'}, status=400)

#     try:
#         districts = DimDistrict.objects.filter(state_id=state_id).order_by('name')
#     except Exception:
#         # defensive fallback: return empty list rather than 500
#         return JsonResponse({'districts': []})

#     result = [{'id': d.id, 'name': d.name} for d in districts]
#     return JsonResponse({'districts': result})

# from django.contrib.auth.decorators import login_required

# @login_required
# def profile(request):
#     user = request.user
#     registrations = Registration.objects.none()
#     try:
#         # If Registration has FK to user named `user`
#         if hasattr(user, 'registration_set'):
#             registrations = user.registration_set.all().order_by('-created_at')
#         else:
#             # fallback match by email if present
#             if getattr(user, 'email', None):
#                 registrations = Registration.objects.filter(email=user.email).order_by('-created_at')
#     except Exception:
#         registrations = Registration.objects.none()

#     return render(request, 'accounts/profile.html', {
#         'registrations': registrations,
#         'user': user,
#     })


# @login_required
# def registration_edit(request, pk):
#     reg = get_object_or_404(Registration, pk=pk)
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES, instance=reg)
#         if form.is_valid():
#             reg = form.save(commit=False)
#             reg.save()
#             form.save_m2m()
#             messages.success(request, "Registration updated successfully.")
#             return redirect(reverse('accounts:profile'))
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = RegistrationForm(instance=reg)

#     return render(request, 'accounts/registration_edit.html', {
#         'form': form,
#         'reg': reg,
#     })

# # def viewLogin(request):
# #     return render(request, 'accounts/login.html')   

# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login
# from django.contrib import messages

# def viewLogin(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             return redirect('/')  # 👈 send to home after login
#         else:
#             messages.error(request, 'Invalid username or password')

#     return render(request, 'accounts/login.html')

# def registration_success(request):
#     return render(request, 'accounts/registration_success.html')


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

def home(request):
    """
    Homepage: Real Race Data + Hero + Results
    """
    # --- SVG ICONS (Kept as is) ---
    svg_register = '''<svg>...</svg>'''
    svg_login = '''<svg>...</svg>'''
    
    # --- FETCH REAL DATA ---
    # We fetch all races ordered by the start date
    # .prefetch_related('registrations') makes the rider count query much faster
    # db_races = Race.objects.all().prefetch_related('registrations').order_by('race_start')
    # Use 'race_registrations' (plural) as defined in your updated RaceRegistration model
    # db_races = Race.objects.all().prefetch_related('race_registrations').order_by('race_start')

    now = timezone.now() 
    db_races = Race.objects.all().prefetch_related('race_registrations', 'events').order_by('race_start')

    # --- DUMMY RESULTS (Keep until you create a Results model) ---
    recent_results = [
        {"event": "Table Mountain Time Trial", "date": "Feb 28, 2026", "results": [{"name": "Liam Jacobs", "time": "2h 14m 32s"}, {"name": "Thabo Molefe", "time": "2h 16m 08s"}, {"name": "Sarah van Niekerk", "time": "2h 18m 45s"}]},
        {"event": "Winelands Classic", "date": "Feb 15, 2026", "results": [{"name": "Nina Botha", "time": "3h 02m 11s"}, {"name": "Chris Dlamini", "time": "3h 04m 50s"}, {"name": "James Le Roux", "time": "3h 07m 22s"}]},
        {"event": "Midlands Meander MTB", "date": "Jan 25, 2026", "results": [{"name": "Ethan Pretorius", "time": "4h 31m 09s"}, {"name": "Zanele Nkosi", "time": "4h 35m 44s"}, {"name": "Pieter du Toit", "time": "4h 38m 01s"}]},
    ]

    context = {
        "races": db_races,  # Passing the real QuerySet now
        "recent_results": recent_results,
        "now": now, # Pass current time to template for status logic
    }
    return render(request, "accounts/home.html", context)


# --- NEW TRAFFIC CONTROLLER ---
@login_required
def check_profile_completion(request):
    """
    Traffic controller: 
    Checks both User and Profile models, then sends the user to the right place.
    """
    user = request.user
    
    # 1. Get or create the profile (Safety check)
    profile, created = Profile.objects.get_or_create(user=user)

    # 2. Check for missing mandatory info
    # We check the User model AND the Profile model phone number
    if not user.first_name or not user.last_name or not profile.phone_number:
        messages.info(request, "Almost there! Please complete your profile details.")
        return redirect('accounts:profile_edit') 

    # 3. If everything is complete, send them to their new Profile Page
    return redirect('accounts:profile')# --- REMAINING VIEWS ---


# def register(request):
#     # Fetch races that are either LIVE NOW or REGISTRATION OPEN
#     now = timezone.now()
#     active_races = Race.objects.filter(
#         registration_start__lte=now,
#         race_start__gte=now.date()
#     )

#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             reg = form.save(commit=False)
#             # You might want to save the selected race to the registration model here
#             # selected_race_id = request.POST.get('race_selection')
#             reg.save()
#             form.save_m2m()
#             messages.success(request, "Registration submitted. Thank you!")
#             return redirect('accounts:registration_success')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = RegistrationForm()
    
#     # Get race_id from URL if coming from Home Page "Register Now"
#     preselected_race_id = request.GET.get('race_id')

#     states = DimState.objects.all().order_by('name')
    
#     return render(request, 'accounts/register.html', {
#         'form': form, 
#         'states': states,
#         'active_races': active_races,  # Pass active races to template
#         'preselected_race_id': preselected_race_id
#     })

# def register(request):
#     """
#     Handles race registration and generates a unique Registration ID 
#     based on the initials of the selected race.
#     """
#     # 1. Fetch active races for the selection dropdown
#     now = timezone.now()
#     active_races = Race.objects.filter(
#         registration_start__lte=now,
#         race_start__gte=now.date()
#     )

#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
        
#         if form.is_valid():
#             # Create the instance but don't save to the database yet
#             reg = form.save(commit=False)
            
#             # Capture the race ID from the dropdown (name="race")
#             selected_race_id = request.POST.get('race')
            
#             if selected_race_id:
#                 try:
#                     # Link the race object to the registration
#                     selected_race = Race.objects.get(id=selected_race_id)
#                     reg.race = selected_race
#                 except Race.DoesNotExist:
#                     messages.error(request, "The selected race is invalid.")
#                     return redirect('accounts:register')

#             # This triggers the model's save() method, which now sees 
#             # the linked race and generates "SGF-0001" instead of "REG-0001"
#             reg.save()
            
#             # Save Many-to-Many fields (like event categories)
#             form.save_m2m()
            
#             messages.success(request, f"Registration for {reg.race.name} submitted!")
            
#             # Redirect to the success page with the newly generated ID
#             return redirect(reverse('accounts:registration_success') + f'?reg_id={reg.registration_id}')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         # Initial GET request: empty form
#         form = RegistrationForm()
    
#     # Handle pre-selection if the user clicked "Register" from a specific race card
#     preselected_race_id = request.GET.get('race_id')
#     states = DimState.objects.all().order_by('name')

#     return render(request, 'accounts/register.html', {


# def register(request):
#     """
#     Handles race registration for multiple events while maintaining
#     a single Bib/Registration ID.
#     """
#     now = timezone.now()
#     # Prefetch events so we can show them in the UI without extra DB hits
#     active_races = Race.objects.filter(
#         registration_start__lte=now,
#         race_start__gte=now.date()
#     ).prefetch_related('events')

#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
        
#         # 1. Get the list of Event IDs from the checkboxes
#         selected_event_ids = request.POST.getlist('selected_events')
        
#         if not selected_event_ids:
#             messages.error(request, "Please select at least one event category.")
#             # Return form with errors
#             states = DimState.objects.all().order_by('name')
#             return render(request, 'accounts/register.html', {
#                 'form': form, 
#                 'states': states, 
#                 'active_races': active_races
#             })

#         if form.is_valid():
#             reg = form.save(commit=False)
            
#             try:
#                 # 2. Use the first selected event to set the Race for the Bib ID prefix
#                 first_event = Event.objects.get(id=selected_event_ids[0])
#                 reg.race = first_event.race
#                 reg.save() # This generates the Registration ID (e.g., CTCC-0001)
#                 form.save_m2m()

#                 # 3. Create the many-to-many links in RaceRegistration
#                 for event_id in selected_event_ids:
#                     event_obj = Event.objects.get(id=event_id)
#                     RaceRegistration.objects.get_or_create(
#                         participant=reg,
#                         event=event_obj,
#                         race=event_obj.race
#                     )
                
#                 messages.success(request, f"Registration for {reg.race.name} submitted!")
#                 return redirect(reverse('accounts:registration_success') + f'?reg_id={reg.registration_id}')
            
#             except Event.DoesNotExist:
#                 messages.error(request, "One of the selected events is invalid.")
#                 return redirect('accounts:register')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = RegistrationForm()
    
#     # --- These must stay for your UI to work ---
#     preselected_race_id = request.GET.get('race_id')
#     states = DimState.objects.all().order_by('name')

#     return render(request, 'accounts/register.html', {
#         'form': form, 
#         'states': states,
#         'active_races': active_races,
#         'preselected_race_id': preselected_race_id
#     })

def register(request):
    """
    Handles race registration for multiple events while maintaining
    a single Bib/Registration ID. Sends confirmation email on success.
    """
    now = timezone.now()
    active_races = Race.objects.filter(
        registration_start__lte=now,
        race_start__gte=now.date()
    ).prefetch_related('events')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        selected_event_ids = request.POST.getlist('selected_events')

        if not selected_event_ids:
            messages.error(request, "Please select at least one event category.")
            states = DimState.objects.all().order_by('name')
            return render(request, 'accounts/register.html', {
                'form': form,
                'states': states,
                'active_races': active_races
            })

        if form.is_valid():
            reg = form.save(commit=False)

            try:
                first_event = Event.objects.get(id=selected_event_ids[0])
                reg.race = first_event.race
                reg.save()
                form.save_m2m()

                for event_id in selected_event_ids:
                    event_obj = Event.objects.get(id=event_id)
                    RaceRegistration.objects.get_or_create(
                        participant=reg,
                        event=event_obj,
                        race=event_obj.race
                    )

                # Send confirmation email
                from .email_utils import send_registration_confirmation
                send_registration_confirmation(reg, request)

                messages.success(request, f"Registration for {reg.race.name} submitted!")
                return redirect(reverse('accounts:registration_success') + f'?reg_id={reg.registration_id}')

            except Event.DoesNotExist:
                messages.error(request, "One of the selected events is invalid.")
                return redirect('accounts:register')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    preselected_race_id = request.GET.get('race_id')
    states = DimState.objects.all().order_by('name')

    return render(request, 'accounts/register.html', {
        'form': form,
        'states': states,
        'active_races': active_races,
        'preselected_race_id': preselected_race_id
    })

@require_GET
def ajax_load_districts(request):
    state_id = request.GET.get('state_id') or request.GET.get('state')
    if not state_id: return JsonResponse({'error': 'state_id required'}, status=400)
    districts = DimDistrict.objects.filter(state_id=state_id).order_by('name')
    result = [{'id': d.id, 'name': d.name} for d in districts]
    return JsonResponse({'districts': result})

@login_required
def profile(request):
    user = request.user
    registrations = Registration.objects.filter(email=user.email).order_by('-created_at')
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

# def registration_success(request):
#     return render(request, 'accounts/registration_success.html')

def registration_success(request):
    # Get the ID from the URL query parameters
    reg_id = request.GET.get('reg_id')
    registration = None
    
    if reg_id:
        # Fetch the specific registration using the new registration_id field
        registration = get_object_or_404(Registration, registration_id=reg_id)
        
    return render(request, 'accounts/registration_success.html', {
        'registration': registration
    })


# @login_required
# def profile_view(request):
#     # This prevents the "RelatedObjectDoesNotExist" error by creating the row if missing
#     profile, created = Profile.objects.get_or_create(user=request.user)
#     return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Fetch all registrations linked to this user's email
    # Using .select_related('race') makes the race name load instantly
    registrations = Registration.objects.filter(email=request.user.email).select_related('race').order_by('-created_at')
    
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'registrations': registrations
    })


@login_required
def profile_edit(request):
    # Ensure profile exists for this user
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # request.FILES is required for the Profile Image to work
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # 1. Save Profile fields (phone, bio, pan, etc.)
            profile_instance = form.save()
            
            # 2. Update the User model fields (first_name, last_name)
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            
            messages.success(request, "Athlete profile updated!")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required # Optional: remove if you want users to view it via a public link
def view_registration_details(request, reg_id):
    """
    Shows the details of a specific registration based on the CTCC-0001 ID.
    """
    registration = get_object_or_404(Registration, registration_id=reg_id)
    
    return render(request, 'accounts/registration_detail.html', {
        'registration': registration
    })