# # app_results/urls.py
# from django.urls import path
# from . import views

# app_name = "app_results"

# urlpatterns = [
#     path("", views.results_list, name="list"),
#     path("update/<int:start_entry_id>/", views.update_participation, name="update"),
    
# ]

# app_results/urls.py
from django.urls import path
from . import views

app_name = "app_results"

urlpatterns = [
    path("", views.results_list, name="list"),
    path("update/<int:start_entry_id>/", views.update_participation, name="update"),
    path("update-lap/<int:start_entry_id>/<int:lap_number>/", views.update_lap, name="update_lap"),
]