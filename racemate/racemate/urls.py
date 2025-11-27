# # racemate/urls.py
# from django.contrib import admin
# from django.urls import path, include
# from accounts import views as accounts_views

# urlpatterns = [
#     path("admin/", admin.site.urls),
#     path("", accounts_views.home, name="home"),
#     path("register/", accounts_views.register, name="register"),
#     path("app_admin/", include("app_admin.urls")),
#     path("accounts/", include("allauth.urls")),
#     path("", include(("accounts.urls", "accounts"), namespace="accounts")),

    
# ]

# racemate/urls.py
from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views
import app_results.views as views

urlpatterns = [
    path("admin/", admin.site.urls),

    # top-level aliases so un-namespaced templates keep working
    path("", accounts_views.home, name="home"),
    path("register/", accounts_views.register, name="register"),
    path("ajax/districts/", accounts_views.ajax_load_districts, name="ajax_load_districts"),

    # also include the accounts app with namespace (keeps accounts:... available)
    #path("", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),

    path('app_admin/', include('app_admin.urls')),
    #path('accounts/', include('django.contrib.auth.urls')), 
    path("", include("pages.urls")),
    path("accounts/", include("allauth.urls")),
    path('', include(('app_bib.urls', 'app_bib'), namespace='app_bib')),
    path('bib/', include('app_bib.urls')),
    path("", include("pages.urls")),
    path("results/", include("app_results.urls")),

]
