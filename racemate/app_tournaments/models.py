
# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils import timezone


# class Tournament(models.Model):
#     name = models.CharField(max_length=255)

#     # For MVP, DimEventType acts as the sport:
#     # Badminton, Pickleball, etc.
#     sport = models.ForeignKey(
#         "app_admin.DimEventType",
#         on_delete=models.PROTECT,
#         related_name="tournaments",
#     )

#     venue = models.CharField(max_length=255)

#     registration_start = models.DateTimeField()
#     registration_end = models.DateTimeField()

#     tournament_start = models.DateTimeField()
#     tournament_end = models.DateTimeField(
#         null=True,
#         blank=True,
#     )

#     description = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ["tournament_start"]

#     def __str__(self):
#         return f"{self.name} — {self.sport.name}"

#     @property
#     def status(self):
#         now = timezone.now()

#         if self.tournament_start <= now:
#             if (
#                 not self.tournament_end
#                 or now <= self.tournament_end
#             ):
#                 return "LIVE NOW"

#         if (
#             self.registration_start
#             <= now
#             <= self.registration_end
#         ):
#             return "REGISTRATION OPEN"

#         if now < self.registration_start:
#             return "COMING SOON"

#         return "REGISTRATION CLOSED"


# class EntryFormat(models.Model):
#     """
#     Admin-configurable formats such as Singles, Doubles or Team.
#     """

#     name = models.CharField(
#         max_length=100,
#         unique=True,
#     )

#     minimum_players = models.PositiveSmallIntegerField(
#         default=1,
#     )

#     maximum_players = models.PositiveSmallIntegerField(
#         default=1,
#     )

#     is_active = models.BooleanField(default=True)

#     class Meta:
#         ordering = ["name"]

#     def clean(self):
#         super().clean()

#         if self.minimum_players < 1:
#             raise ValidationError({
#                 "minimum_players": (
#                     "Minimum players must be at least 1."
#                 )
#             })

#         if self.maximum_players < self.minimum_players:
#             raise ValidationError({
#                 "maximum_players": (
#                     "Maximum players cannot be less than "
#                     "minimum players."
#                 )
#             })

#     def __str__(self):
#         return self.name


# class EntryStatus(models.Model):
#     """
#     Admin-configurable statuses such as:
#     Pending, Confirmed, Waitlisted, Withdrawn, Disqualified.
#     """

#     name = models.CharField(
#         max_length=100,
#         unique=True,
#     )

#     code = models.SlugField(
#         max_length=100,
#         unique=True,
#     )

#     is_active = models.BooleanField(default=True)

#     class Meta:
#         ordering = ["name"]
#         verbose_name_plural = "Entry statuses"

#     def __str__(self):
#         return self.name


# class TournamentEntry(models.Model):
#     tournament_category = models.ForeignKey(
#         "TournamentCategory",
#         on_delete=models.CASCADE,
#         related_name="entries",
#     )

#     registration = models.ForeignKey(
#         "accounts.Registration",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="tournament_entries",
#         help_text=(
#             "The public Registration submission "
#             "that created this entry."
#         ),
#     )

#     status = models.ForeignKey(
#         EntryStatus,
#         on_delete=models.PROTECT,
#         related_name="entries",
#     )

#     # Useful for doubles/team names.
#     # Singles entries can leave this blank.
#     display_name = models.CharField(
#         max_length=255,
#         blank=True,
#     )

#     seed = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text="Optional tournament seed.",
#     )

#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="created_tournament_entries",
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#     )

#     class Meta:
#         ordering = [
#             "tournament_category",
#             "seed",
#             "created_at",
#         ]

#     def __str__(self):
#         if self.display_name:
#             return self.display_name

#         return (
#             f"{self.tournament_category.category.name} "
#             f"Entry #{self.pk or 'New'}"
#         )


# class TournamentEntryPlayer(models.Model):
#     entry = models.ForeignKey(
#         TournamentEntry,
#         on_delete=models.CASCADE,
#         related_name="players",
#     )

#     player = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="tournament_entry_memberships",
#     )

#     position = models.PositiveSmallIntegerField(
#         help_text=(
#             "Player order inside the entry: "
#             "1, 2, 3, etc."
#         )
#     )

#     is_captain = models.BooleanField(default=False)

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )

#     class Meta:
#         ordering = [
#             "entry",
#             "position",
#         ]

#         constraints = [
#             models.UniqueConstraint(
#                 fields=[
#                     "entry",
#                     "player",
#                 ],
#                 name="unique_player_per_tournament_entry",
#             ),
#             models.UniqueConstraint(
#                 fields=[
#                     "entry",
#                     "position",
#                 ],
#                 name="unique_player_position_per_entry",
#             ),
#         ]

#     def clean(self):
#         super().clean()

#         # Let Django's required-field validation handle
#         # an empty position.
#         if self.position is None:
#             return

#         if self.position < 1:
#             raise ValidationError({
#                 "position": (
#                     "Player position must be at least 1."
#                 )
#             })

#         if not self.entry_id:
#             return

#         maximum_players = (
#             self.entry
#             .tournament_category
#             .entry_format
#             .maximum_players
#         )

#         if self.position > maximum_players:
#             raise ValidationError({
#                 "position": (
#                     f"This entry format allows a maximum of "
#                     f"{maximum_players} player(s)."
#                 )
#             })

#     def __str__(self):
#         player_name = self.player.get_full_name()

#         if not player_name:
#             player_name = (
#                 self.player.email
#                 or self.player.username
#             )

#         return (
#             f"{player_name} — "
#             f"{self.entry}"
#         )


# class TournamentCategory(models.Model):

#     class FixtureType(models.TextChoices):
#         KNOCKOUT = "knockout", "Knockout"
#         ROUND_ROBIN = "round_robin", "Round Robin"

#     tournament = models.ForeignKey(
#         Tournament,
#         on_delete=models.CASCADE,
#         related_name="categories",
#     )

#     category = models.ForeignKey(
#         "app_admin.DimEventCategory",
#         on_delete=models.PROTECT,
#         related_name="tournament_categories",
#     )

#     entry_format = models.ForeignKey(
#         EntryFormat,
#         on_delete=models.PROTECT,
#         related_name="tournament_categories",
#     )
#     fixture_type = models.CharField(
#         max_length=20,
#         choices=FixtureType.choices,
#         default=FixtureType.KNOCKOUT,
#         help_text=(
#             "Choose how confirmed entries will be "
#             "paired when fixtures are generated."
#         ),
#     )

#     tournament_format = models.ForeignKey(
#         "TournamentFormat",
#         on_delete=models.PROTECT,
#         related_name="tournament_categories",
#         null=True,
#         blank=True,
#     )

#     scoring_rule = models.ForeignKey(
#         "ScoringRule",
#         on_delete=models.PROTECT,
#         related_name="tournament_categories",
#         null=True,
#         blank=True,
#     )

#     entry_fee = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0,
#     )

#     maximum_entries = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#     )

#     registration_open = models.BooleanField(
#         default=True,
#     )

#     is_active = models.BooleanField(
#         default=True,
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )

#     # Phase 2:
#     # Records when fixture generation was completed.
#     # This helps prevent accidental duplicate generation.
#     fixtures_generated_at = models.DateTimeField(
#         null=True,
#         blank=True,
#         editable=False,
#     )

#     def __str__(self):
#         return (
#             f"{self.tournament.name} — "
#             f"{self.category.name}"
#         )


# class TournamentFormat(models.Model):
#     name = models.CharField(
#         max_length=100,
#         unique=True,
#     )

#     code = models.SlugField(
#         max_length=100,
#         unique=True,
#     )

#     description = models.TextField(blank=True)

#     is_active = models.BooleanField(default=True)

#     class Meta:
#         ordering = ["name"]

#     def __str__(self):
#         return self.name


# class MatchStatus(models.Model):
#     name = models.CharField(
#         max_length=100,
#         unique=True,
#     )

#     code = models.SlugField(
#         max_length=100,
#         unique=True,
#     )

#     is_active = models.BooleanField(default=True)

#     class Meta:
#         ordering = ["name"]
#         verbose_name_plural = "Match statuses"

#     def __str__(self):
#         return self.name


# class Match(models.Model):

#     class BracketSide(models.TextChoices):
#         TOP = "top", "Top Half"
#         BOTTOM = "bottom", "Bottom Half"

#     tournament_round = models.ForeignKey(
#         "TournamentRound",
#         on_delete=models.CASCADE,
#         related_name="matches",
#     )

#     match_number = models.PositiveIntegerField(
#         help_text="Match order within this round.",
#     )

#     # Phase 2:
#     # Position of the match inside the bracket.
#     bracket_slot = models.PositiveIntegerField(
#         null=True,
#         blank=True,
#         help_text=(
#             "Position of this match inside "
#             "the tournament bracket."
#         ),
#     )

#     # Phase 2:
#     # Logical bracket side used by the public bracket template.
#     # The template can display top as blue and bottom as red.
#     bracket_side = models.CharField(
#         max_length=10,
#         choices=BracketSide.choices,
#         blank=True,
#         help_text=(
#             "Bracket half used only for "
#             "fixture display styling."
#         ),
#     )

#     entry_one = models.ForeignKey(
#         "TournamentEntry",
#         on_delete=models.PROTECT,
#         related_name="matches_as_entry_one",
#         null=True,
#         blank=True,
#     )

#     entry_two = models.ForeignKey(
#         "TournamentEntry",
#         on_delete=models.PROTECT,
#         related_name="matches_as_entry_two",
#         null=True,
#         blank=True,
#     )

#     status = models.ForeignKey(
#         "MatchStatus",
#         on_delete=models.PROTECT,
#         related_name="matches",
#     )

#     winner = models.ForeignKey(
#         "TournamentEntry",
#         on_delete=models.SET_NULL,
#         related_name="matches_won",
#         null=True,
#         blank=True,
#     )

#     court = models.ForeignKey(
#         "Court",
#         on_delete=models.PROTECT,
#         related_name="matches",
#         null=True,
#         blank=True,
#     )

#     scheduled_at = models.DateTimeField(
#         null=True,
#         blank=True,
#     )

#     scheduled_end = models.DateTimeField(
#         null=True,
#         blank=True,
#     )

#     started_at = models.DateTimeField(
#         null=True,
#         blank=True,
#     )

#     completed_at = models.DateTimeField(
#         null=True,
#         blank=True,
#     )

#     notes = models.TextField(blank=True)

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#     )

#     class Meta:
#         ordering = [
#             "tournament_round",
#             "match_number",
#         ]

#         constraints = [
#             models.UniqueConstraint(
#                 fields=[
#                     "tournament_round",
#                     "match_number",
#                 ],
#                 name="unique_match_number_per_round",
#             )
#         ]

#     def clean(self):
#         super().clean()

#         tournament_category_id = None
#         tournament_id = None

#         if self.tournament_round_id:
#             tournament_category = (
#                 self.tournament_round
#                 .tournament_category
#             )

#             tournament_category_id = tournament_category.id
#             tournament_id = (
#                 tournament_category.tournament_id
#             )

#         # Prevent the same entry from appearing on both sides.
#         if (
#             self.entry_one_id
#             and self.entry_two_id
#             and self.entry_one_id == self.entry_two_id
#         ):
#             raise ValidationError({
#                 "entry_two": (
#                     "A match cannot contain the same "
#                     "entry twice."
#                 )
#             })

#         # Entry one must belong to the round's category.
#         if (
#             self.entry_one_id
#             and tournament_category_id
#             and (
#                 self.entry_one.tournament_category_id
#                 != tournament_category_id
#             )
#         ):
#             raise ValidationError({
#                 "entry_one": (
#                     "Entry one must belong to the same "
#                     "tournament category as the round."
#                 )
#             })

#         # Entry two must belong to the round's category.
#         if (
#             self.entry_two_id
#             and tournament_category_id
#             and (
#                 self.entry_two.tournament_category_id
#                 != tournament_category_id
#             )
#         ):
#             raise ValidationError({
#                 "entry_two": (
#                     "Entry two must belong to the same "
#                     "tournament category as the round."
#                 )
#             })

#         # Winner must be one of the participating entries.
#         if self.winner_id:
#             valid_winner_ids = {
#                 self.entry_one_id,
#                 self.entry_two_id,
#             }

#             if self.winner_id not in valid_winner_ids:
#                 raise ValidationError({
#                     "winner": (
#                         "Winner must be either entry one "
#                         "or entry two."
#                     )
#                 })

#         # Both schedule times should be provided together.
#         if (
#             self.scheduled_at
#             and not self.scheduled_end
#         ):
#             raise ValidationError({
#                 "scheduled_end": (
#                     "Please provide the scheduled end time."
#                 )
#             })

#         if (
#             self.scheduled_end
#             and not self.scheduled_at
#         ):
#             raise ValidationError({
#                 "scheduled_at": (
#                     "Please provide the scheduled start time."
#                 )
#             })

#         # End time must be after start time.
#         if (
#             self.scheduled_at
#             and self.scheduled_end
#             and self.scheduled_end <= self.scheduled_at
#         ):
#             raise ValidationError({
#                 "scheduled_end": (
#                     "Scheduled end time must be after "
#                     "the scheduled start time."
#                 )
#             })

#         # Court must belong to the same tournament.
#         if (
#             self.court_id
#             and tournament_id
#             and self.court.tournament_id != tournament_id
#         ):
#             raise ValidationError({
#                 "court": (
#                     "The selected court must belong to "
#                     "the same tournament as the match."
#                 )
#             })

#         # Prevent overlapping matches on the same court.
#         if (
#             self.court_id
#             and self.scheduled_at
#             and self.scheduled_end
#         ):
#             overlapping_matches = type(self).objects.filter(
#                 court_id=self.court_id,
#                 scheduled_at__lt=self.scheduled_end,
#                 scheduled_end__gt=self.scheduled_at,
#             )

#             if self.pk:
#                 overlapping_matches = (
#                     overlapping_matches.exclude(
#                         pk=self.pk
#                     )
#                 )

#             if overlapping_matches.exists():
#                 raise ValidationError({
#                     "court": (
#                         "This court is already assigned to "
#                         "another match during the selected time."
#                     )
#                 })

#     def update_winner_from_sets(self):


#             if not self.pk:
#                 return None

#             if not self.tournament_round_id:
#                 return None

#             if (
#                 not self.entry_one_id
#                 or not self.entry_two_id
#             ):
#                 return None

#             scoring_rule = (
#                 self.tournament_round
#                 .tournament_category
#                 .scoring_rule
#             )

#             if not scoring_rule:
#                 return None

#             # Best of 3 requires 2 set wins.
#             # Best of 5 requires 3 set wins.
#             sets_required = (
#                 scoring_rule.best_of_sets // 2
#             ) + 1

#             entry_one_wins = self.sets.filter(
#                 is_completed=True,
#                 winner_id=self.entry_one_id,
#             ).count()

#             entry_two_wins = self.sets.filter(
#                 is_completed=True,
#                 winner_id=self.entry_two_id,
#             ).count()

#             calculated_winner_id = None

#             if entry_one_wins >= sets_required:
#                 calculated_winner_id = self.entry_one_id

#             elif entry_two_wins >= sets_required:
#                 calculated_winner_id = self.entry_two_id

#             previous_winner_id = self.winner_id

#             update_values = {
#                 "winner_id": calculated_winner_id,
#             }

#             # Match has a valid winner.
#             if calculated_winner_id:
#                 completed_status = (
#                     MatchStatus.objects
#                     .filter(
#                         code__iexact="completed",
#                         is_active=True,
#                     )
#                     .first()
#                 )

#                 if not completed_status:
#                     raise ValidationError(
#                         "Create an active Match Status with "
#                         "code 'completed'."
#                     )

#                 update_values.update({
#                     "status_id": completed_status.pk,
#                     "completed_at": (
#                         self.completed_at
#                         or timezone.now()
#                     ),
#                 })

#             # Winner was removed because scores changed/deleted.
#             else:
#                 update_values["completed_at"] = None

#                 current_status_code = ""

#                 if self.status_id:
#                     current_status_code = (
#                         self.status.code
#                         .strip()
#                         .lower()
#                     )

#                 if current_status_code == "completed":
#                     scheduled_status = (
#                         MatchStatus.objects
#                         .filter(
#                             code__iexact="scheduled",
#                             is_active=True,
#                         )
#                         .first()
#                     )

#                     if scheduled_status:
#                         update_values["status_id"] = (
#                             scheduled_status.pk
#                         )

#             # Avoid save recursion.
#             type(self).objects.filter(
#                 pk=self.pk
#             ).update(
#                 **update_values
#             )

#             self.winner_id = calculated_winner_id
#             self.completed_at = update_values.get(
#                 "completed_at"
#             )

#             if "status_id" in update_values:
#                 self.status_id = update_values[
#                     "status_id"
#                 ]

#             # Find the next tournament round.
#             next_round = (
#                 TournamentRound.objects
#                 .filter(
#                     tournament_category=(
#                         self.tournament_round
#                         .tournament_category
#                     ),
#                     round_number=(
#                         self.tournament_round
#                         .round_number + 1
#                     ),
#                 )
#                 .first()
#             )

#             # No next round means this was the final.
#             if not next_round:
#                 return calculated_winner_id

#             current_bracket_slot = (
#                 self.bracket_slot
#                 or self.match_number
#             )

#             next_match_slot = (
#                 current_bracket_slot + 1
#             ) // 2

#             next_match = (
#                 next_round.matches
#                 .filter(
#                     bracket_slot=next_match_slot
#                 )
#                 .first()
#             )

#             if not next_match:
#                 raise ValidationError(
#                     "The next-round match could not be found."
#                 )

#             # Odd source slot advances to entry one.
#             # Even source slot advances to entry two.
#             if current_bracket_slot % 2 == 1:
#                 target_field = "entry_one"
#                 target_id_field = "entry_one_id"

#             else:
#                 target_field = "entry_two"
#                 target_id_field = "entry_two_id"

#             existing_target_id = getattr(
#                 next_match,
#                 target_id_field,
#             )

#             # Remove an old winner when the source result
#             # is edited or deleted.
#             if (
#                 previous_winner_id
#                 and previous_winner_id
#                 != calculated_winner_id
#                 and existing_target_id
#                 == previous_winner_id
#             ):
#                 setattr(
#                     next_match,
#                     target_id_field,
#                     None,
#                 )

#                 next_match.full_clean()

#                 next_match.save(
#                     update_fields=[
#                         target_field,
#                     ]
#                 )

#                 existing_target_id = None

#             # Move the newly calculated winner forward.
#             if calculated_winner_id:
#                 if existing_target_id not in (
#                     None,
#                     calculated_winner_id,
#                 ):
#                     raise ValidationError(
#                         "The next-round bracket position "
#                         "is already occupied by another entry."
#                     )

#                 setattr(
#                     next_match,
#                     target_id_field,
#                     calculated_winner_id,
#                 )

#                 next_match.full_clean()

#                 next_match.save(
#                     update_fields=[
#                         target_field,
#                     ]
#                 )

#             return calculated_winner_id
        
#     def __str__(self):
#         return (
#             f"{self.tournament_round} — "
#             f"Match {self.match_number}"
#         )


# class Court(models.Model):
#     tournament = models.ForeignKey(
#         "Tournament",
#         on_delete=models.CASCADE,
#         related_name="courts",
#     )

#     name = models.CharField(
#         max_length=100,
#         help_text=(
#             "Example: Court 1, Court 2, "
#             "Conference Hall Court"
#         ),
#     )

#     location_note = models.CharField(
#         max_length=255,
#         blank=True,
#     )

#     is_active = models.BooleanField(default=True)

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )

#     class Meta:
#         ordering = [
#             "tournament",
#             "name",
#         ]

#         constraints = [
#             models.UniqueConstraint(
#                 fields=[
#                     "tournament",
#                     "name",
#                 ],
#                 name="unique_court_name_per_tournament",
#             )
#         ]

#     def __str__(self):
#         return (
#             f"{self.tournament.name} — "
#             f"{self.name}"
#         )


# class ScoringRule(models.Model):
#     name = models.CharField(
#         max_length=150,
#         unique=True,
#     )

#     best_of_sets = models.PositiveSmallIntegerField(
#         help_text=(
#             "Example: 3 means best of 3 sets."
#         )
#     )

#     points_to_win_set = models.PositiveSmallIntegerField(
#         help_text=(
#             "Example: 21 for badminton."
#         )
#     )

#     winning_margin = models.PositiveSmallIntegerField(
#         default=2,
#     )

#     maximum_points = models.PositiveSmallIntegerField(
#         null=True,
#         blank=True,
#         help_text=(
#             "Optional score cap, "
#             "such as 30 in badminton."
#         ),
#     )

#     is_active = models.BooleanField(default=True)

#     description = models.TextField(blank=True)

#     class Meta:
#         ordering = ["name"]

#     def clean(self):
#         super().clean()

#         if self.best_of_sets < 1:
#             raise ValidationError({
#                 "best_of_sets": (
#                     "Best of sets must be at least 1."
#                 )
#             })

#         if self.best_of_sets % 2 == 0:
#             raise ValidationError({
#                 "best_of_sets": (
#                     "Best of sets should be an odd number, "
#                     "such as 1, 3 or 5."
#                 )
#             })

#         if self.points_to_win_set < 1:
#             raise ValidationError({
#                 "points_to_win_set": (
#                     "Points required to win "
#                     "must be at least 1."
#                 )
#             })

#         if self.winning_margin < 1:
#             raise ValidationError({
#                 "winning_margin": (
#                     "Winning margin must be at least 1."
#                 )
#             })

#         if (
#             self.maximum_points is not None
#             and (
#                 self.maximum_points
#                 < self.points_to_win_set
#             )
#         ):
#             raise ValidationError({
#                 "maximum_points": (
#                     "Maximum points cannot be less than "
#                     "the normal points required to win."
#                 )
#             })

#     def __str__(self):
#         return self.name


# class MatchSet(models.Model):
#     match = models.ForeignKey(
#         "Match",
#         on_delete=models.CASCADE,
#         related_name="sets",
#     )

#     set_number = models.PositiveSmallIntegerField()

#     entry_one_score = models.PositiveIntegerField(
#         default=0,
#     )

#     entry_two_score = models.PositiveIntegerField(
#         default=0,
#     )

#     is_completed = models.BooleanField(
#         default=False,
#     )

#     winner = models.ForeignKey(
#         "TournamentEntry",
#         on_delete=models.SET_NULL,
#         related_name="sets_won",
#         null=True,
#         blank=True,
#         editable=False,
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True,
#     )

#     class Meta:
#         ordering = [
#             "match",
#             "set_number",
#         ]

#         constraints = [
#             models.UniqueConstraint(
#                 fields=[
#                     "match",
#                     "set_number",
#                 ],
#                 name="unique_set_number_per_match",
#             )
#         ]

#     def calculate_winner(self):
#         if not self.is_completed:
#             return None

#         if not self.match_id:
#             return None

#         if (
#             not self.match.entry_one_id
#             or not self.match.entry_two_id
#         ):
#             return None

#         scoring_rule = (
#             self.match
#             .tournament_round
#             .tournament_category
#             .scoring_rule
#         )

#         if not scoring_rule:
#             return None

#         score_one = self.entry_one_score
#         score_two = self.entry_two_score

#         if (
#             score_one is None
#             or score_two is None
#         ):
#             return None

#         if score_one == score_two:
#             return None

#         highest_score = max(
#             score_one,
#             score_two,
#         )

#         lowest_score = min(
#             score_one,
#             score_two,
#         )

#         # Scores cannot exceed the configured cap.
#         if (
#             scoring_rule.maximum_points is not None
#             and (
#                 highest_score
#                 > scoring_rule.maximum_points
#             )
#         ):
#             return None

#         # At the maximum score cap,
#         # the higher score wins.
#         reached_maximum = (
#             scoring_rule.maximum_points is not None
#             and (
#                 highest_score
#                 == scoring_rule.maximum_points
#             )
#         )

#         # Normal set-winning condition.
#         normal_win = (
#             highest_score
#             >= scoring_rule.points_to_win_set
#             and (
#                 highest_score - lowest_score
#                 >= scoring_rule.winning_margin
#             )
#         )

#         if (
#             not reached_maximum
#             and not normal_win
#         ):
#             return None

#         if score_one > score_two:
#             return self.match.entry_one

#         return self.match.entry_two

#     def clean(self):
#         super().clean()

#         if not self.match_id:
#             return

#         if (
#             not self.match.entry_one_id
#             or not self.match.entry_two_id
#         ):
#             raise ValidationError({
#                 "match": (
#                     "Both match entries must be selected "
#                     "before recording scores."
#                 )
#             })

#         scoring_rule = (
#             self.match
#             .tournament_round
#             .tournament_category
#             .scoring_rule
#         )

#         if not scoring_rule:
#             raise ValidationError({
#                 "match": (
#                     "Assign a scoring rule to the tournament "
#                     "category before recording scores."
#                 )
#             })

#         # Prevent errors when an admin inline row
#         # is incomplete.
#         if self.set_number is None:
#             return

#         if self.set_number < 1:
#             raise ValidationError({
#                 "set_number": (
#                     "Set number must be at least 1."
#                 )
#             })

#         if (
#             self.set_number
#             > scoring_rule.best_of_sets
#         ):
#             raise ValidationError({
#                 "set_number": (
#                     f"This scoring rule allows a maximum of "
#                     f"{scoring_rule.best_of_sets} sets."
#                 )
#             })

#         if (
#             self.entry_one_score is None
#             or self.entry_two_score is None
#         ):
#             return

#         maximum_points = (
#             scoring_rule.maximum_points
#         )

#         if maximum_points is not None:
#             if (
#                 self.entry_one_score
#                 > maximum_points
#             ):
#                 raise ValidationError({
#                     "entry_one_score": (
#                         f"Score cannot exceed "
#                         f"{maximum_points}."
#                     )
#                 })

#             if (
#                 self.entry_two_score
#                 > maximum_points
#             ):
#                 raise ValidationError({
#                     "entry_two_score": (
#                         f"Score cannot exceed "
#                         f"{maximum_points}."
#                     )
#                 })

#         if self.is_completed:
#             calculated_winner = (
#                 self.calculate_winner()
#             )

#             if calculated_winner is None:
#                 raise ValidationError(
#                     "The completed set score does not satisfy "
#                     "the assigned scoring rule."
#                 )

#             self.winner = calculated_winner

#         else:
#             self.winner = None

#     def save(self, *args, **kwargs):
#         """
#         Save the set and recalculate
#         the overall match winner.
#         """

#         self.full_clean()

#         result = super().save(
#             *args,
#             **kwargs
#         )

#         self.match.update_winner_from_sets()

#         return result

#     def delete(self, *args, **kwargs):
#         """
#         Delete the set and recalculate
#         the overall match winner.
#         """

#         match = self.match

#         result = super().delete(
#             *args,
#             **kwargs
#         )

#         match.update_winner_from_sets()

#         return result

#     def __str__(self):
#         return (
#             f"{self.match} — "
#             f"Set {self.set_number}: "
#             f"{self.entry_one_score}-"
#             f"{self.entry_two_score}"
#         )


# class TournamentRound(models.Model):
#     tournament_category = models.ForeignKey(
#         "TournamentCategory",
#         on_delete=models.CASCADE,
#         related_name="rounds",
#     )

#     name = models.CharField(
#         max_length=100,
#         help_text=(
#             "Example: Group Stage, Quarterfinal, "
#             "Semifinal, Final"
#         ),
#     )

#     round_number = models.PositiveIntegerField(
#         help_text=(
#             "Controls the order in which "
#             "rounds are played."
#         )
#     )

#     is_knockout = models.BooleanField(
#         default=False,
#     )

#     is_active = models.BooleanField(
#         default=True,
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True,
#     )

#     class Meta:
#         ordering = [
#             "tournament_category",
#             "round_number",
#         ]

#         constraints = [
#             models.UniqueConstraint(
#                 fields=[
#                     "tournament_category",
#                     "round_number",
#                 ],
#                 name="unique_round_number_per_category",
#             ),
#             models.UniqueConstraint(
#                 fields=[
#                     "tournament_category",
#                     "name",
#                 ],
#                 name="unique_round_name_per_category",
#             ),
#         ]

#     def __str__(self):
#         return (
#             f"{self.tournament_category} — "
#             f"{self.name}"
#         )


from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Tournament(models.Model):
    name = models.CharField(max_length=255)

    # For MVP, DimEventType acts as the sport:
    # Badminton, Pickleball, etc.
    sport = models.ForeignKey(
        "app_admin.DimEventType",
        on_delete=models.PROTECT,
        related_name="tournaments",
    )

    venue = models.CharField(max_length=255)

    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()

    tournament_start = models.DateTimeField()
    tournament_end = models.DateTimeField(
        null=True,
        blank=True,
    )

    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["tournament_start"]

    def __str__(self):
        return f"{self.name} — {self.sport.name}"

    @property
    def status(self):
        now = timezone.now()

        if self.tournament_start <= now:
            if (
                not self.tournament_end
                or now <= self.tournament_end
            ):
                return "LIVE NOW"

        if (
            self.registration_start
            <= now
            <= self.registration_end
        ):
            return "REGISTRATION OPEN"

        if now < self.registration_start:
            return "COMING SOON"

        return "REGISTRATION CLOSED"

class EntryFormat(models.Model):
    """
    Admin-configurable formats such as Singles, Doubles or Team.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    minimum_players = models.PositiveSmallIntegerField(
        default=1,
    )

    maximum_players = models.PositiveSmallIntegerField(
        default=1,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def clean(self):
        super().clean()

        if self.minimum_players < 1:
            raise ValidationError({
                "minimum_players": (
                    "Minimum players must be at least 1."
                )
            })

        if self.maximum_players < self.minimum_players:
            raise ValidationError({
                "maximum_players": (
                    "Maximum players cannot be less than "
                    "minimum players."
                )
            })

    def __str__(self):
        return self.name


class EntryStatus(models.Model):
    """
    Admin-configurable statuses such as:
    Pending, Confirmed, Waitlisted, Withdrawn, Disqualified.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    code = models.SlugField(
        max_length=100,
        unique=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Entry statuses"

    def __str__(self):
        return self.name


class TournamentEntry(models.Model):
    tournament_category = models.ForeignKey(
        "TournamentCategory",
        on_delete=models.CASCADE,
        related_name="entries",
    )

    registration = models.ForeignKey(
        "accounts.Registration",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tournament_entries",
        help_text=(
            "The public Registration submission "
            "that created this entry."
        ),
    )

    status = models.ForeignKey(
        EntryStatus,
        on_delete=models.PROTECT,
        related_name="entries",
    )

    # Useful for doubles/team names.
    # Singles entries can leave this blank.
    display_name = models.CharField(
        max_length=255,
        blank=True,
    )

    seed = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Optional tournament seed.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tournament_entries",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "tournament_category",
            "seed",
            "created_at",
        ]

    def get_display_name(self):
        """Human-readable name for this entry (singles player or doubles pair)."""
        if self.display_name:
            return self.display_name

        names = [
            p.player.get_full_name() or p.player.username
            for p in self.players.all().order_by("position")
        ]
        return " / ".join(names) if names else f"Entry #{self.pk}"

    def __str__(self):
        if self.display_name:
            return self.display_name

        return (
            f"{self.tournament_category.category.name} "
            f"Entry #{self.pk or 'New'}"
        )


class TournamentEntryPlayer(models.Model):
    entry = models.ForeignKey(
        TournamentEntry,
        on_delete=models.CASCADE,
        related_name="players",
    )

    player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tournament_entry_memberships",
    )

    position = models.PositiveSmallIntegerField(
        help_text=(
            "Player order inside the entry: "
            "1, 2, 3, etc."
        )
    )

    is_captain = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "entry",
            "position",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "entry",
                    "player",
                ],
                name="unique_player_per_tournament_entry",
            ),
            models.UniqueConstraint(
                fields=[
                    "entry",
                    "position",
                ],
                name="unique_player_position_per_entry",
            ),
        ]

    def clean(self):
        super().clean()

        # Let Django's required-field validation handle
        # an empty position.
        if self.position is None:
            return

        if self.position < 1:
            raise ValidationError({
                "position": (
                    "Player position must be at least 1."
                )
            })

        if not self.entry_id:
            return

        maximum_players = (
            self.entry
            .tournament_category
            .entry_format
            .maximum_players
        )

        if self.position > maximum_players:
            raise ValidationError({
                "position": (
                    f"This entry format allows a maximum of "
                    f"{maximum_players} player(s)."
                )
            })

    def __str__(self):
        player_name = self.player.get_full_name()

        if not player_name:
            player_name = (
                self.player.email
                or self.player.username
            )

        return (
            f"{player_name} — "
            f"{self.entry}"
        )


class TournamentCategory(models.Model):

    class FixtureType(models.TextChoices):
        KNOCKOUT = "knockout", "Knockout"
        ROUND_ROBIN = "round_robin", "Round Robin"

    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    category = models.ForeignKey(
        "app_admin.DimEventCategory",
        on_delete=models.PROTECT,
        related_name="tournament_categories",
    )

    entry_format = models.ForeignKey(
        EntryFormat,
        on_delete=models.PROTECT,
        related_name="tournament_categories",
    )
    fixture_type = models.CharField(
        max_length=20,
        choices=FixtureType.choices,
        default=FixtureType.KNOCKOUT,
        help_text=(
            "Choose how confirmed entries will be "
            "paired when fixtures are generated."
        ),
    )

    tournament_format = models.ForeignKey(
        "TournamentFormat",
        on_delete=models.PROTECT,
        related_name="tournament_categories",
        null=True,
        blank=True,
    )

    scoring_rule = models.ForeignKey(
        "ScoringRule",
        on_delete=models.PROTECT,
        related_name="tournament_categories",
        null=True,
        blank=True,
    )

    entry_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    maximum_entries = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    registration_open = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # Phase 2:
    # Records when fixture generation was completed.
    # This helps prevent accidental duplicate generation.
    fixtures_generated_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )

    def get_champion(self):
        """
        Returns the winning TournamentEntry for this category, or None
        if the category hasn't finished (no completed final match yet).
        """
        final_round = (
            self.rounds
            .filter(is_active=True)
            .order_by("-round_number")
            .first()
        )
        if not final_round:
            return None

        final_match = (
            final_round.matches
            .filter(winner__isnull=False)
            .order_by("-match_number")
            .first()
        )
        if not final_match:
            return None

        return final_match.winner

    def __str__(self):
        return (
            f"{self.tournament.name} — "
            f"{self.category.name}"
        )


class TournamentFormat(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    code = models.SlugField(
        max_length=100,
        unique=True,
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class MatchStatus(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    code = models.SlugField(
        max_length=100,
        unique=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Match statuses"

    def __str__(self):
        return self.name


class Match(models.Model):

    class BracketSide(models.TextChoices):
        TOP = "top", "Top Half"
        BOTTOM = "bottom", "Bottom Half"

    tournament_round = models.ForeignKey(
        "TournamentRound",
        on_delete=models.CASCADE,
        related_name="matches",
    )

    match_number = models.PositiveIntegerField(
        help_text="Match order within this round.",
    )

    # Phase 2:
    # Position of the match inside the bracket.
    bracket_slot = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Position of this match inside "
            "the tournament bracket."
        ),
    )

    # Phase 2:
    # Logical bracket side used by the public bracket template.
    # The template can display top as blue and bottom as red.
    bracket_side = models.CharField(
        max_length=10,
        choices=BracketSide.choices,
        blank=True,
        help_text=(
            "Bracket half used only for "
            "fixture display styling."
        ),
    )

    entry_one = models.ForeignKey(
        "TournamentEntry",
        on_delete=models.PROTECT,
        related_name="matches_as_entry_one",
        null=True,
        blank=True,
    )

    entry_two = models.ForeignKey(
        "TournamentEntry",
        on_delete=models.PROTECT,
        related_name="matches_as_entry_two",
        null=True,
        blank=True,
    )

    status = models.ForeignKey(
        "MatchStatus",
        on_delete=models.PROTECT,
        related_name="matches",
    )

    winner = models.ForeignKey(
        "TournamentEntry",
        on_delete=models.SET_NULL,
        related_name="matches_won",
        null=True,
        blank=True,
    )

    court = models.ForeignKey(
        "Court",
        on_delete=models.PROTECT,
        related_name="matches",
        null=True,
        blank=True,
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    scheduled_end = models.DateTimeField(
        null=True,
        blank=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "tournament_round",
            "match_number",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tournament_round",
                    "match_number",
                ],
                name="unique_match_number_per_round",
            )
        ]

    def clean(self):
        super().clean()

        tournament_category_id = None
        tournament_id = None

        if self.tournament_round_id:
            tournament_category = (
                self.tournament_round
                .tournament_category
            )

            tournament_category_id = tournament_category.id
            tournament_id = (
                tournament_category.tournament_id
            )

        # Prevent the same entry from appearing on both sides.
        if (
            self.entry_one_id
            and self.entry_two_id
            and self.entry_one_id == self.entry_two_id
        ):
            raise ValidationError({
                "entry_two": (
                    "A match cannot contain the same "
                    "entry twice."
                )
            })

        # Entry one must belong to the round's category.
        if (
            self.entry_one_id
            and tournament_category_id
            and (
                self.entry_one.tournament_category_id
                != tournament_category_id
            )
        ):
            raise ValidationError({
                "entry_one": (
                    "Entry one must belong to the same "
                    "tournament category as the round."
                )
            })

        # Entry two must belong to the round's category.
        if (
            self.entry_two_id
            and tournament_category_id
            and (
                self.entry_two.tournament_category_id
                != tournament_category_id
            )
        ):
            raise ValidationError({
                "entry_two": (
                    "Entry two must belong to the same "
                    "tournament category as the round."
                )
            })

        # Winner must be one of the participating entries.
        if self.winner_id:
            valid_winner_ids = {
                self.entry_one_id,
                self.entry_two_id,
            }

            if self.winner_id not in valid_winner_ids:
                raise ValidationError({
                    "winner": (
                        "Winner must be either entry one "
                        "or entry two."
                    )
                })

        # Both schedule times should be provided together.
        if (
            self.scheduled_at
            and not self.scheduled_end
        ):
            raise ValidationError({
                "scheduled_end": (
                    "Please provide the scheduled end time."
                )
            })

        if (
            self.scheduled_end
            and not self.scheduled_at
        ):
            raise ValidationError({
                "scheduled_at": (
                    "Please provide the scheduled start time."
                )
            })

        # End time must be after start time.
        if (
            self.scheduled_at
            and self.scheduled_end
            and self.scheduled_end <= self.scheduled_at
        ):
            raise ValidationError({
                "scheduled_end": (
                    "Scheduled end time must be after "
                    "the scheduled start time."
                )
            })

        # Court must belong to the same tournament.
        if (
            self.court_id
            and tournament_id
            and self.court.tournament_id != tournament_id
        ):
            raise ValidationError({
                "court": (
                    "The selected court must belong to "
                    "the same tournament as the match."
                )
            })

        # Prevent overlapping matches on the same court.
        if (
            self.court_id
            and self.scheduled_at
            and self.scheduled_end
        ):
            overlapping_matches = type(self).objects.filter(
                court_id=self.court_id,
                scheduled_at__lt=self.scheduled_end,
                scheduled_end__gt=self.scheduled_at,
            )

            if self.pk:
                overlapping_matches = (
                    overlapping_matches.exclude(
                        pk=self.pk
                    )
                )

            if overlapping_matches.exists():
                raise ValidationError({
                    "court": (
                        "This court is already assigned to "
                        "another match during the selected time."
                    )
                })

    def update_winner_from_sets(self):


            if not self.pk:
                return None

            if not self.tournament_round_id:
                return None

            if (
                not self.entry_one_id
                or not self.entry_two_id
            ):
                return None

            scoring_rule = (
                self.tournament_round
                .tournament_category
                .scoring_rule
            )

            if not scoring_rule:
                return None

            # Best of 3 requires 2 set wins.
            # Best of 5 requires 3 set wins.
            sets_required = (
                scoring_rule.best_of_sets // 2
            ) + 1

            entry_one_wins = self.sets.filter(
                is_completed=True,
                winner_id=self.entry_one_id,
            ).count()

            entry_two_wins = self.sets.filter(
                is_completed=True,
                winner_id=self.entry_two_id,
            ).count()

            calculated_winner_id = None

            if entry_one_wins >= sets_required:
                calculated_winner_id = self.entry_one_id

            elif entry_two_wins >= sets_required:
                calculated_winner_id = self.entry_two_id

            previous_winner_id = self.winner_id

            update_values = {
                "winner_id": calculated_winner_id,
            }

            # Match has a valid winner.
            if calculated_winner_id:
                completed_status = (
                    MatchStatus.objects
                    .filter(
                        code__iexact="completed",
                        is_active=True,
                    )
                    .first()
                )

                if not completed_status:
                    raise ValidationError(
                        "Create an active Match Status with "
                        "code 'completed'."
                    )

                update_values.update({
                    "status_id": completed_status.pk,
                    "completed_at": (
                        self.completed_at
                        or timezone.now()
                    ),
                })

            # Winner was removed because scores changed/deleted.
            else:
                update_values["completed_at"] = None

                current_status_code = ""

                if self.status_id:
                    current_status_code = (
                        self.status.code
                        .strip()
                        .lower()
                    )

                if current_status_code == "completed":
                    scheduled_status = (
                        MatchStatus.objects
                        .filter(
                            code__iexact="scheduled",
                            is_active=True,
                        )
                        .first()
                    )

                    if scheduled_status:
                        update_values["status_id"] = (
                            scheduled_status.pk
                        )

            # Avoid save recursion.
            type(self).objects.filter(
                pk=self.pk
            ).update(
                **update_values
            )

            self.winner_id = calculated_winner_id
            self.completed_at = update_values.get(
                "completed_at"
            )

            if "status_id" in update_values:
                self.status_id = update_values[
                    "status_id"
                ]

            # Find the next tournament round.
            next_round = (
                TournamentRound.objects
                .filter(
                    tournament_category=(
                        self.tournament_round
                        .tournament_category
                    ),
                    round_number=(
                        self.tournament_round
                        .round_number + 1
                    ),
                )
                .first()
            )

            # No next round means this was the final.
            if not next_round:
                return calculated_winner_id

            current_bracket_slot = (
                self.bracket_slot
                or self.match_number
            )

            next_match_slot = (
                current_bracket_slot + 1
            ) // 2

            next_match = (
                next_round.matches
                .filter(
                    bracket_slot=next_match_slot
                )
                .first()
            )

            if not next_match:
                raise ValidationError(
                    "The next-round match could not be found."
                )

            # Odd source slot advances to entry one.
            # Even source slot advances to entry two.
            if current_bracket_slot % 2 == 1:
                target_field = "entry_one"
                target_id_field = "entry_one_id"

            else:
                target_field = "entry_two"
                target_id_field = "entry_two_id"

            existing_target_id = getattr(
                next_match,
                target_id_field,
            )

            # Remove an old winner when the source result
            # is edited or deleted.
            if (
                previous_winner_id
                and previous_winner_id
                != calculated_winner_id
                and existing_target_id
                == previous_winner_id
            ):
                setattr(
                    next_match,
                    target_id_field,
                    None,
                )

                next_match.full_clean()

                next_match.save(
                    update_fields=[
                        target_field,
                    ]
                )

                existing_target_id = None

            # Move the newly calculated winner forward.
            if calculated_winner_id:
                if existing_target_id not in (
                    None,
                    calculated_winner_id,
                ):
                    raise ValidationError(
                        "The next-round bracket position "
                        "is already occupied by another entry."
                    )

                setattr(
                    next_match,
                    target_id_field,
                    calculated_winner_id,
                )

                next_match.full_clean()

                next_match.save(
                    update_fields=[
                        target_field,
                    ]
                )

            return calculated_winner_id

    def __str__(self):
        return (
            f"{self.tournament_round} — "
            f"Match {self.match_number}"
        )


class Court(models.Model):
    tournament = models.ForeignKey(
        "Tournament",
        on_delete=models.CASCADE,
        related_name="courts",
    )

    name = models.CharField(
        max_length=100,
        help_text=(
            "Example: Court 1, Court 2, "
            "Conference Hall Court"
        ),
    )

    location_note = models.CharField(
        max_length=255,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "tournament",
            "name",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tournament",
                    "name",
                ],
                name="unique_court_name_per_tournament",
            )
        ]

    def __str__(self):
        return (
            f"{self.tournament.name} — "
            f"{self.name}"
        )


class ScoringRule(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
    )

    best_of_sets = models.PositiveSmallIntegerField(
        help_text=(
            "Example: 3 means best of 3 sets."
        )
    )

    points_to_win_set = models.PositiveSmallIntegerField(
        help_text=(
            "Example: 21 for badminton."
        )
    )

    winning_margin = models.PositiveSmallIntegerField(
        default=2,
    )

    maximum_points = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text=(
            "Optional score cap, "
            "such as 30 in badminton."
        ),
    )

    is_active = models.BooleanField(default=True)

    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def clean(self):
        super().clean()

        if self.best_of_sets < 1:
            raise ValidationError({
                "best_of_sets": (
                    "Best of sets must be at least 1."
                )
            })

        if self.best_of_sets % 2 == 0:
            raise ValidationError({
                "best_of_sets": (
                    "Best of sets should be an odd number, "
                    "such as 1, 3 or 5."
                )
            })

        if self.points_to_win_set < 1:
            raise ValidationError({
                "points_to_win_set": (
                    "Points required to win "
                    "must be at least 1."
                )
            })

        if self.winning_margin < 1:
            raise ValidationError({
                "winning_margin": (
                    "Winning margin must be at least 1."
                )
            })

        if (
            self.maximum_points is not None
            and (
                self.maximum_points
                < self.points_to_win_set
            )
        ):
            raise ValidationError({
                "maximum_points": (
                    "Maximum points cannot be less than "
                    "the normal points required to win."
                )
            })

    def __str__(self):
        return self.name


class MatchSet(models.Model):
    match = models.ForeignKey(
        "Match",
        on_delete=models.CASCADE,
        related_name="sets",
    )

    set_number = models.PositiveSmallIntegerField()

    entry_one_score = models.PositiveIntegerField(
        default=0,
    )

    entry_two_score = models.PositiveIntegerField(
        default=0,
    )

    is_completed = models.BooleanField(
        default=False,
    )

    winner = models.ForeignKey(
        "TournamentEntry",
        on_delete=models.SET_NULL,
        related_name="sets_won",
        null=True,
        blank=True,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "match",
            "set_number",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "match",
                    "set_number",
                ],
                name="unique_set_number_per_match",
            )
        ]

    def calculate_winner(self):
        if not self.is_completed:
            return None

        if not self.match_id:
            return None

        if (
            not self.match.entry_one_id
            or not self.match.entry_two_id
        ):
            return None

        scoring_rule = (
            self.match
            .tournament_round
            .tournament_category
            .scoring_rule
        )

        if not scoring_rule:
            return None

        score_one = self.entry_one_score
        score_two = self.entry_two_score

        if (
            score_one is None
            or score_two is None
        ):
            return None

        if score_one == score_two:
            return None

        highest_score = max(
            score_one,
            score_two,
        )

        lowest_score = min(
            score_one,
            score_two,
        )

        # Scores cannot exceed the configured cap.
        if (
            scoring_rule.maximum_points is not None
            and (
                highest_score
                > scoring_rule.maximum_points
            )
        ):
            return None

        # At the maximum score cap,
        # the higher score wins.
        reached_maximum = (
            scoring_rule.maximum_points is not None
            and (
                highest_score
                == scoring_rule.maximum_points
            )
        )

        # Normal set-winning condition.
        normal_win = (
            highest_score
            >= scoring_rule.points_to_win_set
            and (
                highest_score - lowest_score
                >= scoring_rule.winning_margin
            )
        )

        if (
            not reached_maximum
            and not normal_win
        ):
            return None

        if score_one > score_two:
            return self.match.entry_one

        return self.match.entry_two

    def clean(self):
        super().clean()

        if not self.match_id:
            return

        if (
            not self.match.entry_one_id
            or not self.match.entry_two_id
        ):
            raise ValidationError({
                "match": (
                    "Both match entries must be selected "
                    "before recording scores."
                )
            })

        scoring_rule = (
            self.match
            .tournament_round
            .tournament_category
            .scoring_rule
        )

        if not scoring_rule:
            raise ValidationError({
                "match": (
                    "Assign a scoring rule to the tournament "
                    "category before recording scores."
                )
            })

        # Prevent errors when an admin inline row
        # is incomplete.
        if self.set_number is None:
            return

        if self.set_number < 1:
            raise ValidationError({
                "set_number": (
                    "Set number must be at least 1."
                )
            })

        if (
            self.set_number
            > scoring_rule.best_of_sets
        ):
            raise ValidationError({
                "set_number": (
                    f"This scoring rule allows a maximum of "
                    f"{scoring_rule.best_of_sets} sets."
                )
            })

        if (
            self.entry_one_score is None
            or self.entry_two_score is None
        ):
            return

        maximum_points = (
            scoring_rule.maximum_points
        )

        if maximum_points is not None:
            if (
                self.entry_one_score
                > maximum_points
            ):
                raise ValidationError({
                    "entry_one_score": (
                        f"Score cannot exceed "
                        f"{maximum_points}."
                    )
                })

            if (
                self.entry_two_score
                > maximum_points
            ):
                raise ValidationError({
                    "entry_two_score": (
                        f"Score cannot exceed "
                        f"{maximum_points}."
                    )
                })

        if self.is_completed:
            calculated_winner = (
                self.calculate_winner()
            )

            if calculated_winner is None:
                raise ValidationError(
                    "The completed set score does not satisfy "
                    "the assigned scoring rule."
                )

            self.winner = calculated_winner

        else:
            self.winner = None

    def save(self, *args, **kwargs):
        """
        Save the set and recalculate
        the overall match winner.
        """

        self.full_clean()

        result = super().save(
            *args,
            **kwargs
        )

        self.match.update_winner_from_sets()

        return result

    def delete(self, *args, **kwargs):
        """
        Delete the set and recalculate
        the overall match winner.
        """

        match = self.match

        result = super().delete(
            *args,
            **kwargs
        )

        match.update_winner_from_sets()

        return result

    def __str__(self):
        return (
            f"{self.match} — "
            f"Set {self.set_number}: "
            f"{self.entry_one_score}-"
            f"{self.entry_two_score}"
        )


class TournamentRound(models.Model):
    tournament_category = models.ForeignKey(
        "TournamentCategory",
        on_delete=models.CASCADE,
        related_name="rounds",
    )

    name = models.CharField(
        max_length=100,
        help_text=(
            "Example: Group Stage, Quarterfinal, "
            "Semifinal, Final"
        ),
    )

    round_number = models.PositiveIntegerField(
        help_text=(
            "Controls the order in which "
            "rounds are played."
        )
    )

    is_knockout = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "tournament_category",
            "round_number",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "tournament_category",
                    "round_number",
                ],
                name="unique_round_number_per_category",
            ),
            models.UniqueConstraint(
                fields=[
                    "tournament_category",
                    "name",
                ],
                name="unique_round_name_per_category",
            ),
        ]

    def __str__(self):
        return (
            f"{self.tournament_category} — "
            f"{self.name}"
        )
