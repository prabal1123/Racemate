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
