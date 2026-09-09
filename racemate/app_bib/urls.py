# app_bib/urls.py
from django.urls import path
from .views import RegistrationBibListView
from . import api_views
from . import views

app_name = 'app_bib'

urlpatterns = [
    
    path('registrations/bibs/', RegistrationBibListView.as_view(), name='registration_bib_list'),
    path('start-list/', views.start_list_view, name='start_list'),
    path('start-list/export/', views.start_list_export_csv, name='start_list_export_csv'),  # <-- new
    # path('time-entry/', views.time_entry_list_create, name='time_entry'),
    path('time-entry/', views.time_entry_list_create, name='time_entry_list_create'),
    path('time-entry/', views.time_entry_list_create, name='time_entry'),
    path('registrations/bibs/generate-bibs/', views.generate_bibs_view, name='generate_bibs'),

    path('heat-list/', views.heat_list_view, name='heat_list'),
    path('auto-assign-heats/', views.auto_assign_heats, name='auto_assign_heats'),

    path('start-list/export/', views.start_list_export_csv, name='start_list_export_csv'),
    path('registrations/toggle-collection/<int:reg_id>/', views.toggle_collection, name='toggle_collection'),

    path('api/generate-bulk/', api_views.BulkGenerateBibAPI.as_view(), name='api_generate_bulk'),
    path('api/time-entry/', api_views.TimeEntryAPIView.as_view(), name='api_time_entry'),
    path('start-list/assign-heat/<int:reg_id>/', views.assign_heat, name='assign_heat'),
    path('start-list/toggle/<int:reg_id>/', views.toggle_attendance, name='toggle_attendance'),
]
