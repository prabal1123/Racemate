
# racemate/urls.py
from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Top-level Home/Auth
    path("", accounts_views.home, name="home"),
    # path("register/", accounts_views.register, name="register"),
    path("ajax/districts/", accounts_views.ajax_load_districts, name="ajax_load_districts"),

    # App Routing
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("accounts/", include("allauth.urls")),
    path("app_admin/", include("app_admin.urls")),
    path("app_bib/", include(("app_bib.urls", "app_bib"), namespace="app_bib")),
    path("results/", include(("app_results.urls", "app_results"), namespace="app_results")), # Consistent naming
    path("api/races/", include("app_races.urls")),
    path("pages/", include("pages.urls")), # Removed from root "" to prevent recursion with home
        path(
        'tournaments/',
        include('app_tournaments.urls'),   # ← ye naya line add karo
    ),
]