# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST

from .models import Registration
from .forms import RegistrationForm
from django.utils.safestring import mark_safe

from app_admin.models import DimDistrict, DimState  # used for ajax districts

def home(request):
    """
    Homepage: Welcome hero + Quick Links only (no recent registrations).
    """
    # inline SVG icons (explicit width/height so they stay small)
    svg_file_edit = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="h-6 w-6" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5M16 3l5 5M12 7l5 5" />
    </svg>
    '''
    svg_login = '''
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
        <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
        <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
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

    # Use reverse() when possible — fallback to path if URL name not present
    try:
        register_href = reverse("accounts:register")
    except Exception:
        register_href = "/register/"

    try:
        login_href = reverse("login")
    except Exception:
        login_href = "/accounts/login/"

    try:
        signup_href = reverse("account_signup")
    except Exception:
        signup_href = "/accounts/signup/"

    # Quick links data
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

    context = {
        "quick_links": quick_links,
        "arrow_icon": mark_safe(svg_arrow),
        # No latest_regs provided on purpose — we are removing Recent Registrations
    }
    return render(request, "accounts/home.html", context)

def register(request):
    """
    Public registration form endpoint (basic example).
    Adjust fields and logic to suit your RegistrationForm.
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            reg = form.save(commit=False)
            # perform any pre-save tweaks here (e.g., default category)
            reg.save()
            form.save_m2m()
            messages.success(request, "Registration submitted. Thank you!")
            return redirect(reverse('accounts:home'))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    # supply states for the state select if your form template expects it
    states = DimState.objects.all().order_by('name')
    return render(request, 'accounts/register.html', {
        'form': form,
        'states': states,
    })


@require_GET
def ajax_load_districts(request):
    """
    AJAX endpoint: given ?state_id=XX returns JSON list of districts.
    Returns: [{'id': id, 'name': name}, ...]
    """
    state_id = request.GET.get('state_id') or request.GET.get('state')
    if not state_id:
        return JsonResponse({'error': 'state_id required'}, status=400)

    try:
        districts = DimDistrict.objects.filter(state_id=state_id).order_by('name')
    except Exception:
        # defensive fallback: return empty list rather than 500
        return JsonResponse({'districts': []})

    result = [{'id': d.id, 'name': d.name} for d in districts]
    return JsonResponse({'districts': result})

from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    user = request.user
    registrations = Registration.objects.none()
    try:
        # If Registration has FK to user named `user`
        if hasattr(user, 'registration_set'):
            registrations = user.registration_set.all().order_by('-created_at')
        else:
            # fallback match by email if present
            if getattr(user, 'email', None):
                registrations = Registration.objects.filter(email=user.email).order_by('-created_at')
    except Exception:
        registrations = Registration.objects.none()

    return render(request, 'accounts/profile.html', {
        'registrations': registrations,
        'user': user,
    })


@login_required
def registration_edit(request, pk):
    reg = get_object_or_404(Registration, pk=pk)
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES, instance=reg)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.save()
            form.save_m2m()
            messages.success(request, "Registration updated successfully.")
            return redirect(reverse('accounts:profile'))
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm(instance=reg)

    return render(request, 'accounts/registration_edit.html', {
        'form': form,
        'reg': reg,
    })

# def viewLogin(request):
#     return render(request, 'accounts/login.html')   

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def viewLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')  # 👈 send to home after login
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')
