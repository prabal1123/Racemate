from django.urls import path
from .views import RaceListView

urlpatterns = [
    path('list/', RaceListView.as_view(), name='race-list'),
]