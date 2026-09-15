# # app_results/models.py
# from django.db import models
# from datetime import timedelta

# class Participation(models.Model):
#     # Linked to the Registration model inside accounts app
#     start_entry = models.OneToOneField(
#         "accounts.Registration",
#         on_delete=models.CASCADE,
#         related_name="participation"
#     )

#     is_participated = models.BooleanField(default=False)

#     # Auto-filled from Registration.category or Registration.age_category
#     age_group = models.CharField(max_length=50, blank=True)

#     # Auto-filled on first creation; can be edited later if you want
#     gender = models.CharField(max_length=16, blank=True)

#     total_lap_time = models.DurationField(null=True, blank=True)
#     end_time = models.DateTimeField(null=True, blank=True)

#     certificate_generated = models.BooleanField(default=False)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Participation for {self.start_entry}"


# # app_results/models.py
# from django.db import models
# from datetime import timedelta

# class Participation(models.Model):
#     # existing fields...
#     start_entry = models.OneToOneField(
#         "accounts.Registration",
#         on_delete=models.CASCADE,
#         related_name="participation"
#     )
#     is_collected = models.BooleanField(default=False, help_text="Physical Bib Collection Status")
#     is_participated = models.BooleanField(default=False)
#     age_group = models.CharField(max_length=50, blank=True)
#     gender = models.CharField(max_length=16, blank=True)

#     total_lap_time = models.DurationField(null=True, blank=True)
#     end_time = models.DateTimeField(null=True, blank=True)

#     # NEW: store end time as MM:SS text (keeps UI/display exactly MM:SS)
#     end_time_mmss = models.CharField(max_length=8, null=True, blank=True,
#                                      help_text="Stored as MM:SS (or H:MM:SS for >60min)")

#     certificate_generated = models.BooleanField(default=False)

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)



# app_results/models.py
from django.db import models
from datetime import timedelta

class Participation(models.Model):
    # existing fields...
    start_entry = models.OneToOneField(
        "accounts.Registration",
        on_delete=models.CASCADE,
        related_name="participation"
    )
    is_collected = models.BooleanField(default=False, help_text="Physical Bib Collection Status")
    is_participated = models.BooleanField(default=False)
    age_group = models.CharField(max_length=50, blank=True)
    gender = models.CharField(max_length=16, blank=True)

    total_lap_time = models.DurationField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    # NEW: store end time as MM:SS text (keeps UI/display exactly MM:SS)
    end_time_mmss = models.CharField(max_length=8, null=True, blank=True,
                                     help_text="Stored as MM:SS (or H:MM:SS for >60min)")

    certificate_generated = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Participation for {self.start_entry}"


class LapPlan(models.Model):
    """
    Configures how many lap-timing columns to show for a race, optionally
    scoped to a gender. Different races (and different genders within the
    same race) can require a different number of laps.

    Leave `gender` blank to make a plan apply to every gender in that race
    that doesn't have its own more specific plan.
    """
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    race = models.ForeignKey(
        "app_races.Race",
        on_delete=models.CASCADE,
        related_name="lap_plans",
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        help_text="Leave blank to apply to all genders in this race.",
    )
    laps_required = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('race', 'gender')
        verbose_name = "Lap plan"
        verbose_name_plural = "Lap plans"

    def __str__(self):
        return f"{self.race.name} — {self.gender or 'All genders'} — {self.laps_required} lap(s)"


def get_laps_required(registration):
    """
    Look up how many laps a given registration's race/gender combo requires.
    Falls back to a gender-agnostic plan for the race, then defaults to 1.
    """
    race = getattr(registration, "race", None)
    if not race:
        return 1

    gender = getattr(registration, "gender", None)
    plan = LapPlan.objects.filter(race=race, gender=gender).first()
    if not plan:
        plan = LapPlan.objects.filter(race=race, gender__isnull=True).first()
    return plan.laps_required if plan else 1


class Lap(models.Model):
    """
    One lap-crossing time for a participant. lap_time_mmss stores the
    cumulative elapsed race time (clock reading) at that crossing — the
    same convention the old single "Finish Time" field used. The finish
    time is simply the value of the highest lap_number recorded.
    """
    participation = models.ForeignKey(
        Participation,
        on_delete=models.CASCADE,
        related_name="laps",
    )
    lap_number = models.PositiveIntegerField()
    lap_time_mmss = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        help_text="Cumulative elapsed time at this lap crossing, stored as MM:SS or H:MM:SS.",
    )
    recorded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participation', 'lap_number')
        ordering = ['lap_number']
        verbose_name = "Lap"
        verbose_name_plural = "Laps"

    def __str__(self):
        return f"{self.participation} — Lap {self.lap_number}: {self.lap_time_mmss or '—'}"