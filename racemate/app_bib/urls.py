# app_bib/urls.py
from django.urls import path
from .views import RegistrationBibListView
from . import views

app_name = 'app_bib'

urlpatterns = [
    path('registrations/bibs/', RegistrationBibListView.as_view(), name='registration_bib_list'),
    path('start-list/', views.start_list_view, name='start_list'),
    path('start-list/export/', views.start_list_export_csv, name='start_list_export_csv'),  # <-- new
    path('time-entry/', views.time_entry_list_create, name='time_entry'),
    path('registrations/bibs/generate-bibs/', views.generate_bibs_view, name='generate_bibs'),
]
