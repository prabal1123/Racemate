
# from django.contrib import admin, messages
# from django.core.exceptions import PermissionDenied, ValidationError
# from django.forms.models import (
#     BaseInlineFormSet,
#     inlineformset_factory,
# )
# from django.db import transaction
# from django.db.models import Prefetch
# from django.http import Http404, HttpResponseRedirect, JsonResponse
# from django.template.response import TemplateResponse
# from django.urls import path, reverse

# from app_admin.models import DimEventCategory
# from .services.round_robin_standings import (
#     calculate_round_robin_standings,
# )

# from .models import (
#     Tournament,
#     EntryFormat,
#     TournamentFormat,
#     TournamentCategory,
#     ScoringRule,
#     EntryStatus,
#     TournamentEntry,
#     TournamentEntryPlayer,
#     MatchStatus,
#     TournamentRound,
#     Match,
#     Court,
#     MatchSet,
# )

# from .forms import MatchSetScoreForm
# from .services.fixture_generation import (
#     generate_fixtures,
#     next_power_of_two,
# )

# # =========================================================
# # ENTRY FORMAT
# # =========================================================

# @admin.register(EntryFormat)
# class EntryFormatAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "minimum_players",
#         "maximum_players",
#         "is_active",
#     )

#     list_filter = ("is_active",)
#     search_fields = ("name",)
#     list_editable = ("is_active",)


# # =========================================================
# # TOURNAMENT FORMAT
# # =========================================================

# @admin.register(TournamentFormat)
# class TournamentFormatAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "code",
#         "is_active",
#     )

#     list_filter = ("is_active",)

#     search_fields = (
#         "name",
#         "code",
#     )

#     prepopulated_fields = {
#         "code": ("name",)
#     }


# # =========================================================
# # TOURNAMENT CATEGORY INLINE
# # =========================================================

# class TournamentCategoryInline(admin.TabularInline):
#     model = TournamentCategory
#     extra = 1

#     fields = (
#         "category",
#         "entry_format",
#         "fixture_type",
#         "scoring_rule",
#         "entry_fee",
#         "maximum_entries",
#         "registration_open",
#         "is_active",
#     )


# # =========================================================
# # TOURNAMENT
# # =========================================================

# @admin.register(Tournament)
# class TournamentAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "sport",
#         "venue",
#         "registration_start",
#         "registration_end",
#         "tournament_start",
#         "status",
#     )

#     list_filter = (
#         "sport",
#         "registration_start",
#         "registration_end",
#         "tournament_start",
#     )

#     search_fields = (
#         "name",
#         "venue",
#         "sport__name",
#     )

#     inlines = (
#         TournamentCategoryInline,
#     )

#     def get_queryset(self, request):
#         return (
#             super()
#             .get_queryset(request)
#             .select_related("sport")
#         )

#     def get_urls(self):
#         default_urls = super().get_urls()

#         custom_urls = [
#             path(
#                 "categories-by-sport/",
#                 self.admin_site.admin_view(
#                     self.categories_by_sport
#                 ),
#                 name="app_tournaments_categories_by_sport",
#             ),
#         ]

#         return custom_urls + default_urls

#     def categories_by_sport(self, request):
#         sport_id = request.GET.get("sport_id")

#         if not sport_id:
#             return JsonResponse({
#                 "categories": []
#             })

#         categories = list(
#             DimEventCategory.objects
#             .filter(event_type_id=sport_id)
#             .order_by("name")
#             .values("id", "name")
#         )

#         return JsonResponse({
#             "categories": categories
#         })

#     class Media:
#         js = (
#             "app_tournaments/js/tournament_category_filter.js",
#         )


# # =========================================================
# # TOURNAMENT CATEGORY
# # =========================================================

# class EnrolledTournamentEntryInline(admin.TabularInline):
#     model = TournamentEntry

#     extra = 0
#     can_delete = False
#     show_change_link = False

#     fields = (
#         "entry_name",
#         "enrolled_players",
#         "status",
#         "created_at",
#     )

#     readonly_fields = (
#         "entry_name",
#         "enrolled_players",
#         "status",
#         "created_at",
#     )

#     ordering = (
#         "created_at",
#     )

#     verbose_name = "Enrolled participant"
#     verbose_name_plural = "Enrolled participants"

#     def has_add_permission(
#         self,
#         request,
#         obj=None,
#     ):
#         return False

#     def get_queryset(self, request):
#         player_queryset = (
#             TournamentEntryPlayer.objects
#             .select_related("player")
#             .order_by("position")
#         )

#         return (
#             super()
#             .get_queryset(request)
#             .select_related(
#                 "status",
#                 "registration",
#             )
#             .prefetch_related(
#                 Prefetch(
#                     "players",
#                     queryset=player_queryset,
#                     to_attr="admin_enrolled_players",
#                 )
#             )
#         )

#     @admin.display(description="Entry")
#     def entry_name(self, obj):
#         return (
#             obj.display_name
#             or str(obj.registration)
#         )

#     @admin.display(description="Players")
#     def enrolled_players(self, obj):
#         players = getattr(
#             obj,
#             "admin_enrolled_players",
#             [],
#         )

#         player_names = []

#         for entry_player in players:
#             player = entry_player.player

#             name = (
#                 player.get_full_name().strip()
#                 or player.email
#                 or player.username
#             )

#             player_names.append(
#                 f"{entry_player.position}. {name}"
#             )

#         return " | ".join(player_names) or "No players"
    

# @admin.register(TournamentCategory)
# class TournamentCategoryAdmin(admin.ModelAdmin):
#     change_form_template = (
#         "admin/app_tournaments/"
#         "tournamentcategory/change_form.html"
#     )

#     list_display = (
#         "tournament",
#         "category",
#         "entry_format",
#         "fixture_type",
#         "scoring_rule",
#         "entry_fee",
#         "maximum_entries",
#         "registration_open",
#         "is_active",
#         "fixtures_generated_at",
#     )

#     list_filter = (
#         "tournament",
#         "entry_format",
#         "scoring_rule",
#         "fixture_type",
#         "registration_open",
#         "is_active",
#     )

#     search_fields = (
#         "tournament__name",
#         "category__name",
#         "scoring_rule__name",
#         "entry_format__name",
        
#     )

#     list_select_related = (
#         "tournament",
#         "scoring_rule",
#         "category",
#         "entry_format",
        
#     )

#     readonly_fields = (
#         "fixtures_generated_at",
#     )
#     inlines = (
#         EnrolledTournamentEntryInline,
#     )

#     def get_urls(self):
#         default_urls = super().get_urls()

#         custom_urls = [
#             path(
#                 "<int:object_id>/generate-fixtures/",
#                 self.admin_site.admin_view(
#                     self.generate_fixtures_view
#                 ),
#                 name=(
#                     "app_tournaments_"
#                     "tournamentcategory_generate_fixtures"
#                 ),
#             ),

#             path(
#                 "<int:object_id>/fixture-dashboard/",
#                 self.admin_site.admin_view(
#                     self.fixture_dashboard_view
#                 ),
#                 name=(
#                     "app_tournaments_"
#                     "tournamentcategory_fixture_dashboard"
#                 ),
#             ),

#             path(
#                 "<int:object_id>/results/",
#                 self.admin_site.admin_view(
#                     self.results_view
#                 ),
#                 name=(
#                     "app_tournaments_"
#                     "tournamentcategory_results"
#                 ),
#             ),
#         ]

#         return custom_urls + default_urls

#     def generate_fixtures_view(
#         self,
#         request,
#         object_id,
#     ):
#         tournament_category = self.get_object(
#             request,
#             object_id,
#         )

#         if tournament_category is None:
#             raise Http404(
#                 "Tournament category does not exist."
#             )

#         if not self.has_change_permission(
#             request,
#             tournament_category,
#         ):
#             raise PermissionDenied

#         confirmed_entries = (
#             tournament_category.entries
#             .filter(
#                 status__code__iexact="confirmed"
#             )
#             .count()
#         )

#         fixture_type = (
#             tournament_category.fixture_type
#         )

#         is_knockout = (
#             fixture_type
#             == TournamentCategory.FixtureType.KNOCKOUT
#         )

#         is_round_robin = (
#             fixture_type
#             == TournamentCategory.FixtureType.ROUND_ROBIN
#         )

#         bracket_size = 0
#         bye_count = 0
#         round_robin_match_count = 0

#         # Knockout preview values.
#         if (
#             is_knockout
#             and confirmed_entries >= 2
#         ):
#             bracket_size = next_power_of_two(
#                 confirmed_entries
#             )

#             bye_count = (
#                 bracket_size
#                 - confirmed_entries
#             )

#         # Every entry plays every other entry once.
#         if (
#             is_round_robin
#             and confirmed_entries >= 2
#         ):
#             round_robin_match_count = (
#                 confirmed_entries
#                 * (confirmed_entries - 1)
#                 // 2
#             )

#         validation_problems = []

#         if tournament_category.fixtures_generated_at:
#             validation_problems.append(
#                 "Fixtures have already been generated "
#                 "for this tournament category."
#             )

#         if tournament_category.rounds.exists():
#             validation_problems.append(
#                 "Tournament rounds already exist "
#                 "for this category."
#             )

#         if confirmed_entries < 2:
#             validation_problems.append(
#                 "At least 2 confirmed entries "
#                 "are required."
#             )

#         if not tournament_category.scoring_rule_id:
#             validation_problems.append(
#                 "Scoring rule has not been assigned."
#             )

#         if not (
#             is_knockout
#             or is_round_robin
#         ):
#             validation_problems.append(
#                 "The selected fixture type "
#                 "is not supported."
#             )

#         can_generate = not validation_problems

#         change_url = reverse(
#             (
#                 "admin:"
#                 "app_tournaments_"
#                 "tournamentcategory_change"
#             ),
#             args=[
#                 tournament_category.pk,
#             ],
#         )

#         dashboard_url = reverse(
#             (
#                 "admin:"
#                 "app_tournaments_"
#                 "tournamentcategory_fixture_dashboard"
#             ),
#             args=[
#                 tournament_category.pk,
#             ],
#         )

#         if request.method == "POST":
#             if not can_generate:
#                 self.message_user(
#                     request,
#                     (
#                         "Fixtures cannot be generated. "
#                         + " ".join(
#                             validation_problems
#                         )
#                     ),
#                     level=messages.ERROR,
#                 )

#             else:
#                 try:
#                     result = generate_fixtures(
#                         tournament_category
#                     )

#                 except ValidationError as error:
#                     error_message = " ".join(
#                         error.messages
#                     )

#                     self.message_user(
#                         request,
#                         error_message,
#                         level=messages.ERROR,
#                     )

#                 else:
#                     if is_knockout:
#                         success_message = (
#                             "Knockout fixtures generated "
#                             "successfully. "
#                             f"Confirmed entries: "
#                             f"{result['entry_count']}. "
#                             f"Bracket size: "
#                             f"{result['bracket_size']}. "
#                             f"Rounds created: "
#                             f"{result['rounds_created']}. "
#                             f"First-round matches: "
#                             f"{result['round_one_matches_created']}. "
#                             f"Byes: "
#                             f"{result['bye_count']}."
#                         )

#                     else:
#                         success_message = (
#                             "Round Robin fixtures generated "
#                             "successfully. "
#                             f"Confirmed entries: "
#                             f"{result['entry_count']}. "
#                             f"Matches created: "
#                             f"{result['total_matches_created']}."
#                         )

#                     self.message_user(
#                         request,
#                         success_message,
#                         level=messages.SUCCESS,
#                     )

#                     return HttpResponseRedirect(
#                         dashboard_url
#                     )

#         context = {
#             **self.admin_site.each_context(request),

#             "opts": self.model._meta,
#             "original": tournament_category,
#             "title": "Generate Fixtures",

#             "tournament_category": (
#                 tournament_category
#             ),

#             "fixture_type": fixture_type,
#             "fixture_type_display": (
#                 tournament_category
#                 .get_fixture_type_display()
#             ),

#             "is_knockout": is_knockout,
#             "is_round_robin": is_round_robin,

#             "confirmed_entries": confirmed_entries,

#             "bracket_size": bracket_size,
#             "bye_count": bye_count,

#             "round_robin_match_count": (
#                 round_robin_match_count
#             ),

#             "validation_problems": (
#                 validation_problems
#             ),

#             "can_generate": can_generate,
#             "change_url": change_url,
#             "dashboard_url": dashboard_url,
#         }

#         return TemplateResponse(
#             request,
#             (
#                 "admin/app_tournaments/"
#                 "tournamentcategory/"
#                 "generate_fixtures.html"
#             ),
#             context,
#         )
#     def fixture_dashboard_view(
#         self,
#         request,
#         object_id,
#     ):
#         tournament_category = self.get_object(
#             request,
#             object_id,
#         )

#         if tournament_category is None:
#             raise Http404(
#                 "Tournament category does not exist."
#             )

#         if not self.has_view_permission(
#             request,
#             tournament_category,
#         ):
#             raise PermissionDenied

#         match_queryset = (
#             Match.objects
#             .select_related(
#                 "entry_one",
#                 "entry_two",
#                 "status",
#                 "winner",
#                 "court",
#             )
#             .prefetch_related(
#                 "sets",
#             )
#             .order_by(
#                 "match_number",
#             )
#         )

#         rounds = list(
#             tournament_category.rounds
#             .prefetch_related(
#                 Prefetch(
#                     "matches",
#                     queryset=match_queryset,
#                 )
#             )
#             .order_by(
#                 "round_number",
#             )
#         )

#         all_matches = []

#         for tournament_round in rounds:
#             all_matches.extend(
#                 tournament_round.matches.all()
#             )

#         total_matches = len(all_matches)

#         completed_matches = sum(
#             1
#             for match in all_matches
#             if match.winner_id
#         )

#         pending_matches = (
#             total_matches - completed_matches
#         )

#         change_url = reverse(
#             (
#                 "admin:"
#                 "app_tournaments_"
#                 "tournamentcategory_change"
#             ),
#             args=[
#                 tournament_category.pk,
#             ],
#         )

#         generate_url = reverse(
#             (
#                 "admin:"
#                 "app_tournaments_"
#                 "tournamentcategory_generate_fixtures"
#             ),
#             args=[
#                 tournament_category.pk,
#             ],
#         )

#         results_url = reverse(
#             (
#                 "admin:"
#                 "app_tournaments_"
#                 "tournamentcategory_results"
#             ),
#             args=[
#                 tournament_category.pk,
#             ],
#         )

#         context = {
#             **self.admin_site.each_context(request),
#             "opts": self.model._meta,
#             "title": "Fixture Dashboard",
#             "original": tournament_category,
#             "tournament_category": tournament_category,
#             "rounds": rounds,
#             "total_matches": total_matches,
#             "completed_matches": completed_matches,
#             "pending_matches": pending_matches,
#             "change_url": change_url,
#             "generate_url": generate_url,
#             "results_url": results_url,
#         }

#         return TemplateResponse(
#             request,
#             (
#                 "admin/app_tournaments/"
#                 "tournamentcategory/"
#                 "fixture_dashboard.html"
#             ),
#             context,
#         )
#     def results_view(
#         self,
#         request,
#         object_id,
#     ):
#         tournament_category = self.get_object(
#             request,
#             object_id,
#         )

#         if tournament_category is None:
#             raise Http404(
#                 "Tournament category does not exist."
#             )

#         if not self.has_view_permission(
#             request,
#             tournament_category,
#         ):
#             raise PermissionDenied

#         match_queryset = (
#             Match.objects
#             .select_related(
#                 "entry_one",
#                 "entry_two",
#                 "winner",
#                 "status",
#                 "court",
#             )
#             .prefetch_related(
#                 "sets",
#             )
#             .order_by(
#                 "match_number",
#             )
#         )

#         rounds = list(
#             tournament_category.rounds
#             .prefetch_related(
#                 Prefetch(
#                     "matches",
#                     queryset=match_queryset,
#                 )
#             )
#             .order_by(
#                 "round_number",
#             )
#         )

#         all_matches = []

#         for tournament_round in rounds:
#             all_matches.extend(
#                 tournament_round.matches.all()
#             )

#         completed_matches = [
#             match
#             for match in all_matches
#             if match.winner_id
#         ]

#         champion = None
#         runner_up = None
#         final_match = None
#         standings = None

#         # Knockout result:
#         # Champion and runner-up come from the final match.
#         if (
#             tournament_category.fixture_type
#             == TournamentCategory.FixtureType.KNOCKOUT
#             and rounds
#         ):
#             final_round = rounds[-1]

#             final_match = (
#                 final_round.matches.all().first()
#             )

#             if (
#                 final_match
#                 and final_match.winner_id
#             ):
#                 champion = final_match.winner

#                 if (
#                     final_match.entry_one_id
#                     == final_match.winner_id
#                 ):
#                     runner_up = final_match.entry_two

#                 else:
#                     runner_up = final_match.entry_one

#         # Round Robin result:
#         # Standings table computed from completed matches.
#         elif (
#             tournament_category.fixture_type
#             == TournamentCategory.FixtureType.ROUND_ROBIN
#         ):
#             standings = calculate_round_robin_standings(
#                 tournament_category
#             )

#         change_url = reverse(
#             (
#                 "admin:"
#                 "app_tournaments_"
#                 "tournamentcategory_change"
#             ),
#             args=[
#                 tournament_category.pk,
#             ],
#         )

#         dashboard_url = reverse(
#             (
#                 "admin:"
#                 "app_tournaments_"
#                 "tournamentcategory_fixture_dashboard"
#             ),
#             args=[
#                 tournament_category.pk,
#             ],
#         )

#         context = {
#             **self.admin_site.each_context(request),

#             "opts": self.model._meta,
#             "title": "Tournament Results",
#             "original": tournament_category,

#             "tournament_category": (
#                 tournament_category
#             ),

#             "rounds": rounds,
#             "all_matches": all_matches,
#             "completed_matches": completed_matches,

#             "total_matches": len(all_matches),

#             "completed_match_count": len(
#                 completed_matches
#             ),

#             "remaining_match_count": (
#                 len(all_matches)
#                 - len(completed_matches)
#             ),

#             "champion": champion,
#             "runner_up": runner_up,
#             "final_match": final_match,
#             "standings": standings,

#             "change_url": change_url,
#             "dashboard_url": dashboard_url,
#         }

#         return TemplateResponse(
#             request,
#             (
#                 "admin/app_tournaments/"
#                 "tournamentcategory/"
#                 "results.html"
#             ),
#             context,
#         )
    
# #=======================================================
# # ENTRY STATUS
# # =========================================================

# @admin.register(EntryStatus)
# class EntryStatusAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "code",
#         "is_active",
#     )

#     list_filter = ("is_active",)

#     search_fields = (
#         "name",
#         "code",
#     )

#     prepopulated_fields = {
#         "code": ("name",)
#     }


# # =========================================================
# # TOURNAMENT ENTRY PLAYER VALIDATION
# # =========================================================

# class TournamentEntryPlayerInlineFormSet(BaseInlineFormSet):

#     def clean(self):
#         super().clean()

#         if any(self.errors):
#             return

#         entry = self.instance

#         if not entry.tournament_category_id:
#             return

#         entry_format = (
#             entry
#             .tournament_category
#             .entry_format
#         )

#         player_count = 0
#         selected_players = set()
#         selected_positions = set()

#         for form in self.forms:
#             cleaned_data = getattr(
#                 form,
#                 "cleaned_data",
#                 {}
#             )

#             if not cleaned_data:
#                 continue

#             if cleaned_data.get("DELETE"):
#                 continue

#             player = cleaned_data.get("player")
#             position = cleaned_data.get("position")

#             if not player:
#                 continue

#             player_count += 1

#             if player.pk in selected_players:
#                 raise ValidationError(
#                     "The same player cannot be added twice."
#                 )

#             selected_players.add(player.pk)

#             if position in selected_positions:
#                 raise ValidationError(
#                     "Each player must have a different position."
#                 )

#             selected_positions.add(position)

#         minimum_players = entry_format.minimum_players
#         maximum_players = entry_format.maximum_players

#         if player_count < minimum_players:
#             raise ValidationError(
#                 f"{entry_format.name} requires at least "
#                 f"{minimum_players} player(s)."
#             )

#         if player_count > maximum_players:
#             raise ValidationError(
#                 f"{entry_format.name} allows a maximum of "
#                 f"{maximum_players} player(s)."
#             )


# class TournamentEntryPlayerInline(admin.TabularInline):
#     model = TournamentEntryPlayer
#     formset = TournamentEntryPlayerInlineFormSet

#     extra = 1

#     fields = (
#         "player",
#         "position",
#         "is_captain",
#     )

#     autocomplete_fields = (
#         "player",
#     )


# # =========================================================
# # TOURNAMENT ENTRY
# # =========================================================

# @admin.register(TournamentEntry)
# class TournamentEntryAdmin(admin.ModelAdmin):
#     list_display = (
#         "entry_name",
#         "tournament_category",
#         "status",
#         "seed",
#         "created_at",
#     )

#     list_filter = (
#         "tournament_category__tournament",
#         "tournament_category__category",
#         "tournament_category__tournament_format",
#         "status",
#         "created_at",
#     )

#     search_fields = (
#         "display_name",
#         "tournament_category__tournament__name",
#         "tournament_category__category__name",
#         "players__player__first_name",
#         "players__player__last_name",
#         "players__player__email",
#         "players__player__username",
#     )

#     autocomplete_fields = (
#         "tournament_category",
#         "status",
#     )

#     inlines = (
#         TournamentEntryPlayerInline,
#     )

#     def get_queryset(self, request):
#         return (
#             super()
#             .get_queryset(request)
#             .select_related(
#                 "tournament_category",
#                 "tournament_category__tournament",
#                 "tournament_category__category",
#                 "status",
#             )
#         )

#     @admin.display(description="Entry")
#     def entry_name(self, obj):
#         return obj.display_name or str(obj)

#     def save_model(
#         self,
#         request,
#         obj,
#         form,
#         change,
#     ):
#         if not obj.created_by_id:
#             obj.created_by = request.user

#         super().save_model(
#             request,
#             obj,
#             form,
#             change,
#         )

# @admin.register(MatchStatus)
# class MatchStatusAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "code",
#         "is_active",
#     )

#     list_filter = ("is_active",)

#     search_fields = (
#         "name",
#         "code",
#     )

#     prepopulated_fields = {
#         "code": ("name",)
#     }

# # =========================================================
# # COURT ADMIN
# # =========================================================

# @admin.register(Court)
# class CourtAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "tournament",
#         "location_note",
#         "is_active",
#     )

#     list_filter = (
#         "tournament",
#         "is_active",
#     )

#     search_fields = (
#         "name",
#         "tournament__name",
#         "location_note",
#     )

#     list_editable = (
#         "is_active",
#     )

#     list_select_related = (
#         "tournament",
#     )

#     ordering = (
#         "tournament",
#         "name",
#     )



# @admin.register(ScoringRule)
# class ScoringRuleAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "best_of_sets",
#         "points_to_win_set",
#         "winning_margin",
#         "maximum_points",
#         "is_active",
#     )

#     list_filter = ("is_active",)

#     search_fields = ("name",)

#     list_editable = ("is_active",)


# class MatchSetInline(admin.TabularInline):
#     model = MatchSet
#     extra = 1

#     fields = (
#         "set_number",
#         "entry_one_score",
#         "entry_two_score",
#         "is_completed",
#         "winner",
#     )

#     readonly_fields = (
#         "winner",
#     )

#     ordering = (
#         "set_number",
#     )

#     def get_max_num(self, request, obj=None, **kwargs):
#         if not obj or not obj.tournament_round_id:
#             return 0

#         scoring_rule = (
#             obj.tournament_round
#             .tournament_category
#             .scoring_rule
#         )

#         if scoring_rule:
#             return scoring_rule.best_of_sets

#         return 0
# # =========================================================
# # MATCH ADMIN
# # =========================================================

# @admin.register(Match)
# class MatchAdmin(admin.ModelAdmin):
#     list_display = (
#         "match_number",
#         "tournament_round",
#         "entry_one",
#         "entry_two",
#         "court",
#         "status",
#         "winner",
#         "scheduled_at",
#         "scheduled_end",
#     )

#     list_filter = (
#         "tournament_round__tournament_category__tournament",
#         "tournament_round__tournament_category__category",
#         "tournament_round",
#         "court",
#         "status",
#         "scheduled_at",
#     )

#     search_fields = (
#         "entry_one__display_name",
#         "entry_two__display_name",
#         "winner__display_name",
#         "tournament_round__name",
#         "tournament_round__tournament_category__tournament__name",
#         "tournament_round__tournament_category__category__name",
#         "court__name",
#     )

#     autocomplete_fields = (
#         "tournament_round",
#         "entry_one",
#         "entry_two",
#         "status",
#         "winner",
#         "court",
#     )

#     list_select_related = (
#         "tournament_round",
#         "tournament_round__tournament_category",
#         "tournament_round__tournament_category__tournament",
#         "tournament_round__tournament_category__category",
#         "entry_one",
#         "entry_two",
#         "court",
#         "status",
#         "winner",
#     )

#     inlines = (
#         MatchSetInline,
#     )
#     ordering = (
#         "tournament_round",
#         "match_number",
#     )

#     def get_urls(self):
#         default_urls = super().get_urls()

#         custom_urls = [
#             path(
#                 "<int:object_id>/score/",
#                 self.admin_site.admin_view(
#                     self.score_match_view
#                 ),
#                 name=(
#                     "app_tournaments_"
#                     "match_score"
#                 ),
#             ),
#         ]

#         return custom_urls + default_urls

#     def score_match_view(
#         self,
#         request,
#         object_id,
#     ):
#         match = self.get_object(
#             request,
#             object_id,
#         )

#         if match is None:
#             raise Http404(
#                 "Match does not exist."
#             )

#         if not self.has_change_permission(
#             request,
#             match,
#         ):
#             raise PermissionDenied

#         match = (
#             Match.objects
#             .select_related(
#                 "tournament_round",
#                 "tournament_round__tournament_category",
#                 "tournament_round__tournament_category__tournament",
#                 "tournament_round__tournament_category__category",
#                 "tournament_round__tournament_category__scoring_rule",
#                 "entry_one",
#                 "entry_two",
#                 "status",
#                 "winner",
#             )
#             .get(pk=match.pk)
#         )

#         change_url = reverse(
#             "admin:app_tournaments_match_change",
#             args=[match.pk],
#         )

#         tournament_category = (
#             match.tournament_round
#             .tournament_category
#         )

#         dashboard_url = reverse(
#             (
#                 "admin:"
#                 "app_tournaments_"
#                 "tournamentcategory_fixture_dashboard"
#             ),
#             args=[tournament_category.pk],
#         )

#         if (
#             not match.entry_one_id
#             or not match.entry_two_id
#         ):
#             self.message_user(
#                 request,
#                 (
#                     "Both match participants must be "
#                     "available before entering scores."
#                 ),
#                 level=messages.ERROR,
#             )

#             return HttpResponseRedirect(
#                 dashboard_url
#             )

#         scoring_rule = (
#             tournament_category.scoring_rule
#         )

#         if not scoring_rule:
#             self.message_user(
#                 request,
#                 (
#                     "Assign a scoring rule before "
#                     "entering match scores."
#                 ),
#                 level=messages.ERROR,
#             )

#             return HttpResponseRedirect(
#                 change_url
#             )

#         best_of_sets = (
#             scoring_rule.best_of_sets
#         )

#         existing_sets = (
#             MatchSet.objects
#             .filter(match=match)
#             .order_by("set_number")
#         )

#         existing_set_numbers = set(
#             existing_sets.values_list(
#                 "set_number",
#                 flat=True,
#             )
#         )

#         missing_set_numbers = [
#             set_number
#             for set_number in range(
#                 1,
#                 best_of_sets + 1,
#             )
#             if (
#                 set_number
#                 not in existing_set_numbers
#             )
#         ]

#         MatchSetFormSet = inlineformset_factory(
#             Match,
#             MatchSet,
#             form=MatchSetScoreForm,
#             fields=(
#                 "set_number",
#                 "entry_one_score",
#                 "entry_two_score",
#                 "is_completed",
#             ),
#             extra=len(missing_set_numbers),
#             can_delete=False,
#             max_num=best_of_sets,
#             validate_max=True,
#         )

#         initial_data = [
#             {
#                 "set_number": set_number,
#             }
#             for set_number in missing_set_numbers
#         ]

#         formset = MatchSetFormSet(
#             data=(
#                 request.POST
#                 if request.method == "POST"
#                 else None
#             ),
#             instance=match,
#             queryset=existing_sets,
#             initial=initial_data,
#             prefix="sets",
#         )

#         if request.method == "POST":
#             if formset.is_valid():
#                 try:
#                     with transaction.atomic():
#                         formset.save()

#                 except ValidationError as error:
#                     self.message_user(
#                         request,
#                         " ".join(error.messages),
#                         level=messages.ERROR,
#                     )

#                 else:
#                     match.refresh_from_db()

#                     if match.winner_id:
#                         success_message = (
#                             "Scores saved successfully. "
#                             f"Winner: {match.winner}."
#                         )
#                     else:
#                         success_message = (
#                             "Scores saved successfully. "
#                             "The match is not completed yet."
#                         )

#                     self.message_user(
#                         request,
#                         success_message,
#                         level=messages.SUCCESS,
#                     )

#                     return HttpResponseRedirect(
#                         dashboard_url
#                     )

#         context = {
#             **self.admin_site.each_context(request),
#             "opts": self.model._meta,
#             "title": "Enter Match Score",
#             "original": match,
#             "match": match,
#             "formset": formset,
#             "scoring_rule": scoring_rule,
#             "dashboard_url": dashboard_url,
#             "change_url": change_url,
#         }

#         return TemplateResponse(
#             request,
#             (
#                 "admin/app_tournaments/"
#                 "match/score_form.html"
#             ),
#             context,
#         )

#     fieldsets = (
#         (
#             "Match details",
#             {
#                 "fields": (
#                     "tournament_round",
#                     "match_number",
#                     "entry_one",
#                     "entry_two",
#                     "status",
#                     "winner",
#                 )
#             },
#         ),

#         (
#             "Schedule",
#             {
#                 "fields": (
#                     "court",
#                     "scheduled_at",
#                     "scheduled_end",
#                     "started_at",
#                     "completed_at",
#                 )
#             },
#         ),
#         (
#             "Additional information",
#             {
#                 "fields": (
#                     "notes",
#                 )
#             },
#         ),
#     )

# @admin.register(TournamentRound)
# class TournamentRoundAdmin(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "tournament_category",
#         "round_number",
#         "is_knockout",
#         "is_active",
#     )

#     list_filter = (
#         "tournament_category__tournament",
#         "tournament_category__category",
#         "is_knockout",
#         "is_active",
#     )

#     search_fields = (
#         "name",
#         "tournament_category__tournament__name",
#         "tournament_category__category__name",
#     )

#     autocomplete_fields = (
#         "tournament_category",
#     )

#     ordering = (
#         "tournament_category",
#         "round_number",
#     )


from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.db.models import Prefetch
from django.http import JsonResponse
from django.urls import path

from app_admin.models import DimEventCategory

from .models import (
    Tournament,
    EntryFormat,
    TournamentFormat,
    TournamentCategory,
    ScoringRule,
    EntryStatus,
    TournamentEntry,
    TournamentEntryPlayer,
    MatchStatus,
    TournamentRound,
    Match,
    Court,
    MatchSet,
)


# =========================================================
# ENTRY FORMAT
# =========================================================

@admin.register(EntryFormat)
class EntryFormatAdmin(admin.ModelAdmin):
    list_display = ("name", "minimum_players", "maximum_players", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active",)


# =========================================================
# TOURNAMENT FORMAT
# =========================================================

@admin.register(TournamentFormat)
class TournamentFormatAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    prepopulated_fields = {"code": ("name",)}


# =========================================================
# TOURNAMENT CATEGORY INLINE
# =========================================================

class TournamentCategoryInline(admin.TabularInline):
    model = TournamentCategory
    extra = 1
    fields = (
        "category",
        "entry_format",
        "fixture_type",
        "scoring_rule",
        "entry_fee",
        "maximum_entries",
        "registration_open",
        "is_active",
    )


# =========================================================
# TOURNAMENT
# =========================================================

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = (
        "name", "sport", "venue",
        "registration_start", "registration_end",
        "tournament_start", "status",
    )
    list_filter = ("sport", "registration_start", "registration_end", "tournament_start")
    search_fields = ("name", "venue", "sport__name")
    inlines = (TournamentCategoryInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("sport")

    def get_urls(self):
        default_urls = super().get_urls()
        custom_urls = [
            path(
                "categories-by-sport/",
                self.admin_site.admin_view(self.categories_by_sport),
                name="app_tournaments_categories_by_sport",
            ),
        ]
        return custom_urls + default_urls

    def categories_by_sport(self, request):
        sport_id = request.GET.get("sport_id")
        if not sport_id:
            return JsonResponse({"categories": []})

        categories = list(
            DimEventCategory.objects
            .filter(event_type_id=sport_id)
            .order_by("name")
            .values("id", "name")
        )
        return JsonResponse({"categories": categories})

    class Media:
        js = ("app_tournaments/js/tournament_category_filter.js",)


# =========================================================
# TOURNAMENT CATEGORY
# =========================================================

class EnrolledTournamentEntryInline(admin.TabularInline):
    model = TournamentEntry
    extra = 0
    can_delete = False
    show_change_link = False
    fields = ("entry_name", "enrolled_players", "status", "created_at")
    readonly_fields = ("entry_name", "enrolled_players", "status", "created_at")
    ordering = ("created_at",)
    verbose_name = "Enrolled participant"
    verbose_name_plural = "Enrolled participants"

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        player_queryset = (
            TournamentEntryPlayer.objects
            .select_related("player")
            .order_by("position")
        )
        return (
            super().get_queryset(request)
            .select_related("status", "registration")
            .prefetch_related(
                Prefetch("players", queryset=player_queryset, to_attr="admin_enrolled_players")
            )
        )

    @admin.display(description="Entry")
    def entry_name(self, obj):
        return obj.display_name or str(obj.registration)

    @admin.display(description="Players")
    def enrolled_players(self, obj):
        players = getattr(obj, "admin_enrolled_players", [])
        player_names = []
        for entry_player in players:
            player = entry_player.player
            name = player.get_full_name().strip() or player.email or player.username
            player_names.append(f"{entry_player.position}. {name}")
        return " | ".join(player_names) or "No players"


@admin.register(TournamentCategory)
class TournamentCategoryAdmin(admin.ModelAdmin):
    change_form_template = (
        "admin/app_tournaments/tournamentcategory/change_form.html"
    )

    list_display = (
        "tournament", "category", "entry_format", "fixture_type",
        "scoring_rule", "entry_fee", "maximum_entries",
        "registration_open", "is_active", "fixtures_generated_at",
    )
    list_filter = (
        "tournament", "entry_format", "scoring_rule",
        "fixture_type", "registration_open", "is_active",
    )
    search_fields = (
        "tournament__name", "category__name",
        "scoring_rule__name", "entry_format__name",
    )
    list_select_related = ("tournament", "scoring_rule", "category", "entry_format")
    readonly_fields = ("fixtures_generated_at",)
    inlines = (EnrolledTournamentEntryInline,)


# =========================================================
# ENTRY STATUS
# =========================================================

@admin.register(EntryStatus)
class EntryStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    prepopulated_fields = {"code": ("name",)}


# =========================================================
# TOURNAMENT ENTRY PLAYER VALIDATION
# =========================================================

class TournamentEntryPlayerInlineFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()
        if any(self.errors):
            return

        entry = self.instance
        if not entry.tournament_category_id:
            return

        entry_format = entry.tournament_category.entry_format
        player_count = 0
        selected_players = set()
        selected_positions = set()

        for form in self.forms:
            cleaned_data = getattr(form, "cleaned_data", {})
            if not cleaned_data or cleaned_data.get("DELETE"):
                continue

            player = cleaned_data.get("player")
            position = cleaned_data.get("position")
            if not player:
                continue

            player_count += 1

            if player.pk in selected_players:
                raise ValidationError("The same player cannot be added twice.")
            selected_players.add(player.pk)

            if position in selected_positions:
                raise ValidationError("Each player must have a different position.")
            selected_positions.add(position)

        minimum_players = entry_format.minimum_players
        maximum_players = entry_format.maximum_players

        if player_count < minimum_players:
            raise ValidationError(f"{entry_format.name} requires at least {minimum_players} player(s).")
        if player_count > maximum_players:
            raise ValidationError(f"{entry_format.name} allows a maximum of {maximum_players} player(s).")


class TournamentEntryPlayerInline(admin.TabularInline):
    model = TournamentEntryPlayer
    formset = TournamentEntryPlayerInlineFormSet
    extra = 1
    fields = ("player", "position", "is_captain")
    autocomplete_fields = ("player",)


# =========================================================
# TOURNAMENT ENTRY
# =========================================================

@admin.register(TournamentEntry)
class TournamentEntryAdmin(admin.ModelAdmin):
    list_display = ("entry_name", "tournament_category", "status", "seed", "created_at")
    list_filter = (
        "tournament_category__tournament", "tournament_category__category",
        "tournament_category__tournament_format", "status", "created_at",
    )
    search_fields = (
        "display_name", "tournament_category__tournament__name",
        "tournament_category__category__name",
        "players__player__first_name", "players__player__last_name",
        "players__player__email", "players__player__username",
    )
    autocomplete_fields = ("tournament_category", "status")
    inlines = (TournamentEntryPlayerInline,)

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related(
                "tournament_category",
                "tournament_category__tournament",
                "tournament_category__category",
                "status",
            )
        )

    @admin.display(description="Entry")
    def entry_name(self, obj):
        return obj.display_name or str(obj)

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MatchStatus)
class MatchStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    prepopulated_fields = {"code": ("name",)}


# =========================================================
# COURT ADMIN
# =========================================================

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ("name", "tournament", "location_note", "is_active")
    list_filter = ("tournament", "is_active")
    search_fields = ("name", "tournament__name", "location_note")
    list_editable = ("is_active",)
    list_select_related = ("tournament",)
    ordering = ("tournament", "name")


@admin.register(ScoringRule)
class ScoringRuleAdmin(admin.ModelAdmin):
    list_display = (
        "name", "best_of_sets", "points_to_win_set",
        "winning_margin", "maximum_points", "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_editable = ("is_active",)


class MatchSetInline(admin.TabularInline):
    model = MatchSet
    extra = 1
    fields = ("set_number", "entry_one_score", "entry_two_score", "is_completed", "winner")
    readonly_fields = ("winner",)
    ordering = ("set_number",)

    def get_max_num(self, request, obj=None, **kwargs):
        if not obj or not obj.tournament_round_id:
            return 0
        scoring_rule = obj.tournament_round.tournament_category.scoring_rule
        return scoring_rule.best_of_sets if scoring_rule else 0


# =========================================================
# MATCH ADMIN
# =========================================================

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "match_number", "tournament_round", "entry_one", "entry_two",
        "court", "status", "winner", "scheduled_at", "scheduled_end",
    )
    list_filter = (
        "tournament_round__tournament_category__tournament",
        "tournament_round__tournament_category__category",
        "tournament_round", "court", "status", "scheduled_at",
    )
    search_fields = (
        "entry_one__display_name", "entry_two__display_name", "winner__display_name",
        "tournament_round__name",
        "tournament_round__tournament_category__tournament__name",
        "tournament_round__tournament_category__category__name",
        "court__name",
    )
    autocomplete_fields = ("tournament_round", "entry_one", "entry_two", "status", "winner", "court")
    list_select_related = (
        "tournament_round", "tournament_round__tournament_category",
        "tournament_round__tournament_category__tournament",
        "tournament_round__tournament_category__category",
        "entry_one", "entry_two", "court", "status", "winner",
    )
    inlines = (MatchSetInline,)
    ordering = ("tournament_round", "match_number")

    fieldsets = (
        ("Match details", {
            "fields": ("tournament_round", "match_number", "entry_one", "entry_two", "status", "winner")
        }),
        ("Schedule", {
            "fields": ("court", "scheduled_at", "scheduled_end", "started_at", "completed_at")
        }),
        ("Additional information", {"fields": ("notes",)}),
    )


@admin.register(TournamentRound)
class TournamentRoundAdmin(admin.ModelAdmin):
    list_display = ("name", "tournament_category", "round_number", "is_knockout", "is_active")
    list_filter = (
        "tournament_category__tournament", "tournament_category__category",
        "is_knockout", "is_active",
    )
    search_fields = (
        "name", "tournament_category__tournament__name", "tournament_category__category__name",
    )
    autocomplete_fields = ("tournament_category",)
    ordering = ("tournament_category", "round_number")