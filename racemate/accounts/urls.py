
# accounts/urls.py
from django.urls import path, include
from . import views
from app_admin import views as admin_views
from django.contrib.auth.views import LogoutView
from . import api_views
from .api_views import UserProfileAPIView
app_name = 'accounts'

urlpatterns = [
    # --- Public Pages ---
    path('', views.home, name='home'),
    # path('register/', views.register, name='register'),
        path('register/event/<uuid:event_uuid>/', views.register_race_event, name='register_race_event'),
    path('register/tournament-category/<uuid:category_uuid>/', views.register_tournament_category, name='register_tournament_category'),
    path('ajax/districts/', views.ajax_load_districts, name='ajax_load_districts'),
    path('registration-success/', views.registration_success, name='registration_success'),
    
    # --- THE MISSING PATH: View Registration Details ---
    # This matches the link in your success and profile pages
    path('registration/view/<str:reg_id>/', views.view_registration_details, name='view_registration_details'),

    # --- Profile Management ---
    path('check-profile/', views.check_profile_completion, name='check_profile'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('registration/edit/<int:pk>/', views.registration_edit, name='registration_edit'),

    # --- Authentication ---
    path('login/', views.viewLogin, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    # --- Admin / Analysis ---
    path('analysis/', admin_views.analysis_dashboard, name='analysis_dashboard'),
    path('api/analysis/summary/', admin_views.api_analysis_summary, name='api_analysis_summary'),
    path('analysis/export/csv/', admin_views.analysis_export_csv, name='analysis_export_csv'),
    path('app_admin/', include('app_admin.urls')),

    # --- API Endpoints ---
    path('api/login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('api/logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),
    path('api/me/', api_views.MeAPIView.as_view(), name='api_me'),
    path('api/token/refresh/', api_views.CookieTokenRefreshView.as_view(), name='api_token_refresh'),
    path('api/send-otp/', api_views.SendEmailOTPAPIView.as_view(), name='send_otp'),
    path('api/verify-otp/', api_views.VerifyEmailOTPAPIView.as_view(), name='verify_otp'),
    path('api/profile/', UserProfileAPIView.as_view(), name='api-profile'),

    # Add these two lines to accounts/urls.py, inside urlpatterns,
# near the existing ajax_load_districts path.

    path('ajax/tournament-categories/', views.ajax_tournament_categories, name='ajax_tournament_categories'),
    path('ajax/partner-search/', views.ajax_partner_search, name='ajax_partner_search'),

    path(
    "register/tournament/<uuid:tournament_uuid>/",
    views.register_tournament,
    name="register_tournament",
    ),
    path(
    "register/race/<uuid:race_uuid>/type/<int:event_type_id>/",
    views.register_race_by_type,
    name="register_race_by_type",
),
]


