
# # accounts/urls.py
# from django.urls import path, include
# from . import views
# from app_admin import views as admin_views 
# app_name = 'accounts'

# urlpatterns = [
#     path('', views.home, name='home'),          # home page
#     path('register/', views.register, name='register'),
#     path('ajax/districts/', views.ajax_load_districts, name='ajax_load_districts'),

#     # analysis dashboard & APIs (staff-only)
#     path('admin/analysis/', views.analysis_dashboard, name='analysis_dashboard'),
#     path('admin/api/analysis/summary/', views.api_analysis_summary, name='api_analysis_summary'),
#     path('admin/analysis/export/csv/', views.analysis_export_csv, name='analysis_export_csv'),

#     # keep other app routes (e.g., link to app_admin)
#     path('app_admin/', include('app_admin.urls')),
# ]

# accounts/urls.py
from django.urls import path, include
from . import views
from app_admin import views as admin_views  # correctly import admin views
from django.contrib.auth.views import LogoutView

app_name = 'accounts'

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),                     # home page
    path('register/', views.register, name='register'),    # registration form
    path('ajax/districts/', views.ajax_load_districts, name='ajax_load_districts'),

    path('analysis/', admin_views.analysis_dashboard, name='analysis_dashboard'),
    path('api/analysis/summary/', admin_views.api_analysis_summary, name='api_analysis_summary'),
    path('analysis/export/csv/', admin_views.analysis_export_csv, name='analysis_export_csv'),

    # Other admin app URLs
    path('app_admin/', include('app_admin.urls')),
    path("", views.home, name="home"),
    

    # Optional: user-facing profile pages
    path('profile/', views.profile, name='profile'),
    path('profile/edit/<int:pk>/', views.registration_edit, name='registration_edit'),
    #path('login/', views.viewLogin, name='login'),
    path('accounts/login/',views.viewLogin,name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]
