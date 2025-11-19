# from django.urls import path
# from . import shell,views
# urlpatterns = [
#     path('populate_dim_date/', shell.populate_dim_date, name='populate_dim_date'),
#     path('registrations/', views.registration_list, name='registration_list'),
#     path('registrations/edit/<int:pk>/', views.registration_edit, name='registration_edit'),
#     path('registrations/delete/<int:pk>/', views.registration_delete, name='registration_delete'),
    
# ]

from django.urls import path
from . import shell, views

# app_name = 'app_admin'

urlpatterns = [
    path('populate_dim_date/', shell.populate_dim_date, name='populate_dim_date'),

    # Analysis / reporting (moved here from accounts to avoid admin/ collision)
    path('analysis/', views.analysis_dashboard, name='analysis_dashboard'),
    path('analysis/export/csv/', views.analysis_export_csv, name='analysis_export_csv'),
    path('api/analysis/summary/', views.api_analysis_summary, name='api_analysis_summary'),

    # Registrations management
    path('registrations/', views.registration_list, name='registration_list'),
    path('registrations/edit/<int:pk>/', views.registration_edit, name='registration_edit'),
    path('registrations/delete/<int:pk>/', views.registration_delete, name='registration_delete'),
]
