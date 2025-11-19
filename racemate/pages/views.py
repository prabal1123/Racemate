# from django.shortcuts import render
# from django.urls import reverse
# from allauth.socialaccount import providers as allauth_providers

# def home(request):
#     links = [
#         {"title": "Register", "description": "Register for upcoming events", "href": reverse("accounts:register")},
#         {"title": "Account Login", "description": "Sign in to your account", "href": reverse("account_login")},
#         {"title": "Sign up", "description": "Create a new account", "href": reverse("account_signup")},
#     ]

#     try:
#         available_providers = allauth_providers.registry.get_list()
#     except Exception:
#         available_providers = []

#     return render(request, "home.html", {
#         "links": links,
#         "available_providers": available_providers,
#     })

# # app/views.py
# from django.shortcuts import render

# def quick_links_page(request):
#     links = [
#         {"icon": "file-edit", "title": "Register", "description": "Register for upcoming events", "href": "/register"},
#         {"icon": "log-in",    "title": "Account Login", "description": "Sign in to your account",    "href": "/login"},
#         {"icon": "user-plus",  "title": "Sign up",        "description": "Create a new account",      "href": "/signup"},
#     ]
#     return render(request, "partials/quick_links_page.html", {"links": links})



# app_pages/views.py
from django.shortcuts import render
from django.urls import reverse
from django.utils.safestring import mark_safe

def home(request):
    """
    Homepage: Welcome hero + Quick Links only (no recent registrations).
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

    context = {
        "quick_links": quick_links,
        "arrow_icon": mark_safe(svg_arrow),
        # add other homepage context (hero, announcements) as needed
    }
    return render(request, "pages/home.html", context)
