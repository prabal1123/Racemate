from django.urls import path
from . import views

app_name = "app_tournaments"

urlpatterns = [
    path("categories/<int:category_id>/fixtures/", views.public_fixture_view, name="public_fixture"),

    path("staff/login/", views.staff_login_view, name="staff_login"),

    path("categories/<int:object_id>/generate/", views.generate_fixtures_view, name="generate_fixtures"),
    path("categories/<int:object_id>/dashboard/", views.fixture_dashboard_view, name="fixture_dashboard"),
    path("categories/<int:object_id>/results/", views.results_view, name="results"),
    path("matches/<int:object_id>/score/", views.score_match_view, name="score_match"),
    path("", views.tournament_list_view, name="tournament_list"),
    path("create/", views.tournament_create_view, name="tournament_create"),
    path("<int:pk>/edit/", views.tournament_edit_view, name="tournament_edit"),
    path("entries/", views.tournament_entry_list_view, name="tournament_entry_list"),
    path("entries/<int:pk>/edit/", views.tournament_entry_edit_view, name="tournament_entry_edit"),
    path("categories-list/", views.tournament_category_list_view, name="tournament_category_list"),
    path("categories-list/<int:pk>/edit/", views.tournament_category_edit_view, name="tournament_category_edit"),
    path("matches/", views.match_list_view, name="match_list"),
]