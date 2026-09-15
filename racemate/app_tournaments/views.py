from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import render

from .models import (
    Match,
    TournamentCategory,
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from .models import TournamentCategory, Match, MatchSet
from .forms import MatchSetScoreForm
from .services.fixture_generation import generate_fixtures, next_power_of_two
from .services.round_robin_standings import calculate_round_robin_standings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

from .models import TournamentCategory, Match, MatchSet
from .forms import MatchSetScoreForm
from .services.fixture_generation import generate_fixtures, next_power_of_two
from .services.round_robin_standings import calculate_round_robin_standings

from .models import Tournament,TournamentCategory
from .models import Tournament,TournamentCategory
from .forms import TournamentForm, TournamentCategoryFormSet,TournamentEntryForm,TournamentCategoryForm
from .models import TournamentEntry, TournamentCategory, EntryStatus
from .models import Match, MatchStatus, TournamentCategory

def staff_required(view_func):
    """Only logged-in staff can access — redirect to existing accounts login page."""
    decorated = login_required(view_func, login_url="accounts:login")
    decorated = user_passes_test(
        lambda u: u.is_staff, login_url="accounts:login"
    )(decorated)
    return decorated


def staff_login_view(request):
    from django.contrib.auth import authenticate, login as auth_login

    next_url = request.GET.get("next") or request.POST.get("next") or "app_tournaments:tournament_list"

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            auth_login(request, user)
            return redirect(next_url)

        messages.error(request, "Invalid credentials, or you don't have staff access.")

    return render(request, "app_tournaments/staff_login.html", {"next": next_url})


# =========================================================
# GENERATE FIXTURES
# =========================================================
@staff_required
def generate_fixtures_view(request, object_id):
    tournament_category = get_object_or_404(TournamentCategory, pk=object_id)

    confirmed_entries = tournament_category.entries.filter(
        status__code__iexact="confirmed"
    ).count()

    fixture_type = tournament_category.fixture_type
    is_knockout = fixture_type == TournamentCategory.FixtureType.KNOCKOUT
    is_round_robin = fixture_type == TournamentCategory.FixtureType.ROUND_ROBIN

    bracket_size = bye_count = round_robin_match_count = 0

    if is_knockout and confirmed_entries >= 2:
        bracket_size = next_power_of_two(confirmed_entries)
        bye_count = bracket_size - confirmed_entries

    if is_round_robin and confirmed_entries >= 2:
        round_robin_match_count = confirmed_entries * (confirmed_entries - 1) // 2

    validation_problems = []

    if tournament_category.fixtures_generated_at:
        validation_problems.append("Fixtures have already been generated for this tournament category.")
    if tournament_category.rounds.exists():
        validation_problems.append("Tournament rounds already exist for this category.")
    if confirmed_entries < 2:
        validation_problems.append("At least 2 confirmed entries are required.")
    if not tournament_category.scoring_rule_id:
        validation_problems.append("Scoring rule has not been assigned.")
    if not (is_knockout or is_round_robin):
        validation_problems.append("The selected fixture type is not supported.")

    can_generate = not validation_problems

    dashboard_url = reverse("app_tournaments:fixture_dashboard", args=[tournament_category.pk])

    if request.method == "POST":
        if not can_generate:
            messages.error(request, "Fixtures cannot be generated. " + " ".join(validation_problems))
        else:
            try:
                result = generate_fixtures(tournament_category)
            except ValidationError as error:
                messages.error(request, " ".join(error.messages))
            else:
                if is_knockout:
                    messages.success(
                        request,
                        f"Knockout fixtures generated successfully. "
                        f"Confirmed entries: {result['entry_count']}. "
                        f"Bracket size: {result['bracket_size']}. "
                        f"Rounds created: {result['rounds_created']}. "
                        f"First-round matches: {result['round_one_matches_created']}. "
                        f"Byes: {result['bye_count']}.",
                    )
                else:
                    messages.success(
                        request,
                        f"Round Robin fixtures generated successfully. "
                        f"Confirmed entries: {result['entry_count']}. "
                        f"Matches created: {result['total_matches_created']}.",
                    )
                return redirect(dashboard_url)

    context = {
        "tournament_category": tournament_category,
        "fixture_type": fixture_type,
        "fixture_type_display": tournament_category.get_fixture_type_display(),
        "is_knockout": is_knockout,
        "is_round_robin": is_round_robin,
        "confirmed_entries": confirmed_entries,
        "bracket_size": bracket_size,
        "bye_count": bye_count,
        "round_robin_match_count": round_robin_match_count,
        "validation_problems": validation_problems,
        "can_generate": can_generate,
        "dashboard_url": dashboard_url,
    }

    return render(request, "admin/app_tournaments/tournamentcategory/generate_fixtures.html", context)


# =========================================================
# FIXTURE DASHBOARD
# =========================================================
@staff_required
def fixture_dashboard_view(request, object_id):
    tournament_category = get_object_or_404(TournamentCategory, pk=object_id)

    match_queryset = Match.objects.select_related(
        "entry_one", "entry_two", "status", "winner", "court"
    ).prefetch_related("sets").order_by("match_number")

    rounds = list(
        tournament_category.rounds.prefetch_related(
            Prefetch("matches", queryset=match_queryset)
        ).order_by("round_number")
    )

    all_matches = [m for r in rounds for m in r.matches.all()]
    total_matches = len(all_matches)
    completed_matches = sum(1 for m in all_matches if m.winner_id)
    pending_matches = total_matches - completed_matches
    change_url = reverse("app_tournaments:tournament_category_edit", args=[tournament_category.pk])
    context = {
        "tournament_category": tournament_category,
        "rounds": rounds,
        "total_matches": total_matches,
        "completed_matches": completed_matches,
        "pending_matches": pending_matches,
        "generate_url": reverse("app_tournaments:generate_fixtures", args=[tournament_category.pk]),
        "results_url": reverse("app_tournaments:results", args=[tournament_category.pk]),
        "change_url": change_url,
    }

    return render(request, "admin/app_tournaments/tournamentcategory/fixture_dashboard.html", context)


# =========================================================
# RESULTS
# =========================================================

def results_view(request, object_id):
    tournament_category = get_object_or_404(TournamentCategory, pk=object_id)

    match_queryset = Match.objects.select_related(
        "entry_one", "entry_two", "winner", "status", "court"
    ).prefetch_related("sets").order_by("match_number")

    rounds = list(
        tournament_category.rounds.prefetch_related(
            Prefetch("matches", queryset=match_queryset)
        ).order_by("round_number")
    )

    all_matches = [m for r in rounds for m in r.matches.all()]
    completed_matches = [m for m in all_matches if m.winner_id]

    champion = runner_up = final_match = standings = None

    if tournament_category.fixture_type == TournamentCategory.FixtureType.KNOCKOUT and rounds:
        final_match = rounds[-1].matches.all().first()
        if final_match and final_match.winner_id:
            champion = final_match.winner
            runner_up = (
                final_match.entry_two
                if final_match.entry_one_id == final_match.winner_id
                else final_match.entry_one
            )
    elif tournament_category.fixture_type == TournamentCategory.FixtureType.ROUND_ROBIN:
        standings = calculate_round_robin_standings(tournament_category)

    context = {
        "tournament_category": tournament_category,
        "rounds": rounds,
        "all_matches": all_matches,
        "completed_matches": completed_matches,
        "total_matches": len(all_matches),
        "completed_match_count": len(completed_matches),
        "remaining_match_count": len(all_matches) - len(completed_matches),
        "champion": champion,
        "runner_up": runner_up,
        "final_match": final_match,
        "standings": standings,
        "dashboard_url": reverse("app_tournaments:fixture_dashboard", args=[tournament_category.pk]),
    }

    return render(request, "admin/app_tournaments/tournamentcategory/results.html", context)


# =========================================================
# SCORE ENTRY
# =========================================================
@staff_required
def score_match_view(request, object_id):
    match = get_object_or_404(
        Match.objects.select_related(
            "tournament_round",
            "tournament_round__tournament_category",
            "tournament_round__tournament_category__scoring_rule",
            "entry_one", "entry_two", "status", "winner",
        ),
        pk=object_id,
    )

    tournament_category = match.tournament_round.tournament_category
    dashboard_url = reverse("app_tournaments:fixture_dashboard", args=[tournament_category.pk])

    if not match.entry_one_id or not match.entry_two_id:
        messages.error(request, "Both match participants must be available before entering scores.")
        return redirect(dashboard_url)

    scoring_rule = tournament_category.scoring_rule
    if not scoring_rule:
        messages.error(request, "Assign a scoring rule before entering match scores.")
        return redirect(dashboard_url)

    best_of_sets = scoring_rule.best_of_sets
    existing_sets = MatchSet.objects.filter(match=match).order_by("set_number")
    existing_set_numbers = set(existing_sets.values_list("set_number", flat=True))
    missing_set_numbers = [n for n in range(1, best_of_sets + 1) if n not in existing_set_numbers]

    MatchSetFormSet = inlineformset_factory(
        Match, MatchSet, form=MatchSetScoreForm,
        fields=("set_number", "entry_one_score", "entry_two_score", "is_completed"),
        extra=len(missing_set_numbers), can_delete=False,
        max_num=best_of_sets, validate_max=True,
    )

    initial_data = [{"set_number": n} for n in missing_set_numbers]

    formset = MatchSetFormSet(
        data=request.POST if request.method == "POST" else None,
        instance=match, queryset=existing_sets,
        initial=initial_data, prefix="sets",
    )

    if request.method == "POST" and formset.is_valid():
        try:
            with transaction.atomic():
                formset.save()
        except ValidationError as error:
            messages.error(request, " ".join(error.messages))
        else:
            match.refresh_from_db()
            if match.winner_id:
                messages.success(request, f"Scores saved successfully. Winner: {match.winner}.")
            else:
                messages.success(request, "Scores saved successfully. The match is not completed yet.")
            return redirect(dashboard_url)

    context = {
        "match": match,
        "formset": formset,
        "scoring_rule": scoring_rule,
        "dashboard_url": dashboard_url,
    }

    return render(request, "admin/app_tournaments/match/score_form.html", context)


def public_fixture_view(request, category_id):
    """
    Public, read-only fixture/bracket page.
    No login required.

    Score-entry links are shown only to staff users,
    who will be asked to log in via the admin
    when they click through.
    """
    try:
        tournament_category = (
            TournamentCategory.objects
            .select_related(
                "tournament",
                "category",
                "scoring_rule",
            )
            .get(pk=category_id)
        )

    except TournamentCategory.DoesNotExist:
        raise Http404(
            "Tournament category does not exist."
        )

    match_queryset = (
        Match.objects
        .select_related(
            "entry_one",
            "entry_two",
            "status",
            "winner",
        )
        .order_by(
            "match_number",
        )
    )

    rounds = list(
        tournament_category.rounds
        .prefetch_related(
            Prefetch(
                "matches",
                queryset=match_queryset,
            )
        )
        .order_by(
            "round_number",
        )
    )

    context = {
        "tournament_category": tournament_category,
        "rounds": rounds,
        "is_staff_viewer": (
            request.user.is_authenticated
            and request.user.is_staff
        ),
    }

    return render(
        request,
        "app_tournaments/public_fixture.html",
        context,
    )


@staff_required
def tournament_list_view(request):
    tournaments = (
        Tournament.objects
        .select_related("sport")
        .prefetch_related("categories")
        .order_by("-tournament_start")
    )

    return render(
        request,
        "app_tournaments/tournament_list.html",
        {"tournaments": tournaments},
    )


@staff_required
def tournament_create_view(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        formset = TournamentCategoryFormSet(request.POST, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            tournament = form.save()
            formset.instance = tournament
            formset.save()

            messages.success(request, f"Tournament '{tournament.name}' created successfully.")
            return redirect("app_tournaments:tournament_list")
    else:
        form = TournamentForm()
        formset = TournamentCategoryFormSet()

    return render(
        request,
        "app_tournaments/tournament_form.html",
        {"form": form, "formset": formset, "title": "Create Tournament"},
    )

@staff_required
def tournament_edit_view(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)


    if request.method == "POST":
        form = TournamentForm(request.POST, instance=tournament)
        formset = TournamentCategoryFormSet(request.POST, instance=tournament)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            messages.success(request, f"Tournament '{tournament.name}' updated successfully.")
            return redirect("app_tournaments:tournament_list")
    else:
        form = TournamentForm(instance=tournament)
        formset = TournamentCategoryFormSet(instance=tournament)

    return render(
        request,
        "app_tournaments/tournament_form.html",
        {"form": form, "formset": formset, "title": f"Edit — {tournament.name}", "tournament": tournament},
    )


@staff_required
def tournament_entry_list_view(request):
    entries = (
        TournamentEntry.objects
        .select_related(
            "tournament_category",
            "tournament_category__tournament",
            "tournament_category__category",
            "status",
        )
        .prefetch_related("players__player")
        .order_by("-created_at")
    )

    category_id = request.GET.get("category")
    status_id = request.GET.get("status")

    if category_id:
        entries = entries.filter(tournament_category_id=category_id)

    if status_id:
        entries = entries.filter(status_id=status_id)

    context = {
        "entries": entries,
        "categories": TournamentCategory.objects.select_related("tournament", "category").order_by("tournament__name"),
        "statuses": EntryStatus.objects.filter(is_active=True),
        "selected_category": category_id,
        "selected_status": status_id,
    }

    return render(request, "app_tournaments/tournament_entry_list.html", context)


@staff_required
def tournament_entry_edit_view(request, pk):
    entry = get_object_or_404(
        TournamentEntry.objects.select_related("tournament_category"),
        pk=pk,
    )

    if request.method == "POST":
        form = TournamentEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Entry updated successfully.")
            return redirect("app_tournaments:tournament_entry_list")
    else:
        form = TournamentEntryForm(instance=entry)

    return render(
        request,
        "app_tournaments/tournament_entry_form.html",
        {"form": form, "entry": entry},
    )

@staff_required
def tournament_category_list_view(request):
    categories = (
        TournamentCategory.objects
        .select_related(
            "tournament", "category", "entry_format",
            "scoring_rule",
        )
        .order_by("-created_at")
    )

    tournament_id = request.GET.get("tournament")
    if tournament_id:
        categories = categories.filter(tournament_id=tournament_id)

    context = {
        "categories": categories,
        "tournaments": Tournament.objects.order_by("name"),
        "selected_tournament": tournament_id,
    }

    return render(request, "app_tournaments/tournament_category_list.html", context)


@staff_required
def tournament_category_edit_view(request, pk):
    category = get_object_or_404(
        TournamentCategory.objects.select_related("tournament", "category"),
        pk=pk,
    )

    if request.method == "POST":
        form = TournamentCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Tournament category updated successfully.")
            return redirect("app_tournaments:tournament_category_list")
    else:
        form = TournamentCategoryForm(instance=category)

    return render(
        request,
        "app_tournaments/tournament_category_form.html",
        {"form": form, "category": category},
    )


@staff_required
def match_list_view(request):
    matches = (
        Match.objects
        .select_related(
            "tournament_round",
            "tournament_round__tournament_category",
            "tournament_round__tournament_category__tournament",
            "entry_one",
            "entry_two",
            "status",
            "winner",
            "court",
        )
        .order_by("-tournament_round__tournament_category_id", "tournament_round__round_number", "match_number")
    )

    category_id = request.GET.get("category")
    status_id = request.GET.get("status")

    if category_id:
        matches = matches.filter(tournament_round__tournament_category_id=category_id)

    if status_id:
        matches = matches.filter(status_id=status_id)

    context = {
        "matches": matches,
        "categories": TournamentCategory.objects.select_related("tournament", "category").order_by("tournament__name"),
        "statuses": MatchStatus.objects.filter(is_active=True),
        "selected_category": category_id,
        "selected_status": status_id,
    }

    return render(request, "app_tournaments/match_list.html", context)
