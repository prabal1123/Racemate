
# # app_races/models.py
# from django.db import models
# from django.utils import timezone
# import uuid

# class Race(models.Model):
#     name = models.CharField(max_length=255)
#     location = models.CharField(max_length=255)
#     distance_km = models.PositiveIntegerField()
#     registration_start = models.DateTimeField()
#     race_start = models.DateTimeField()

#     def __str__(self):
#         return self.name

#     @property
#     def status(self):
#         now = timezone.now()
#         if now.date() == self.race_start.date():
#             return "LIVE NOW"
#         elif self.registration_start <= now < self.race_start:
#             return "REGISTRATION OPEN"
#         return "COMING SOON"

# # class Event(models.Model):
# #     race = models.ForeignKey(
# #         Race,
# #         related_name='events',
# #         on_delete=models.CASCADE
# #     )

# #     category = models.ForeignKey(
# #         "app_admin.DimEventCategory",
# #         on_delete=models.PROTECT,
# #         related_name="race_events",
# #         null=True,
# #         blank=True
# #     )

# #     title = models.CharField(max_length=255)
# #     distance_km = models.PositiveIntegerField(null=True, blank=True)
# #     price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
# #     description = models.TextField(blank=True)

# #     def __str__(self):
# #         return f"{self.race.name} - {self.title}"

# class Event(models.Model):
#     race = models.ForeignKey(
#         Race,
#         related_name='events',
#         on_delete=models.CASCADE
#     )

#     category = models.ForeignKey(
#         "app_admin.DimEventCategory",
#         on_delete=models.PROTECT,
#         related_name="race_events",
#         null=True,
#         blank=True
#     )

#     title = models.CharField(max_length=255)
#     distance_km = models.PositiveIntegerField(null=True, blank=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     description = models.TextField(blank=True)

#     # Public, unguessable identifier used in this event's shareable,
#     # single-event registration link: /register/event/<uuid>/
#     uuid = models.UUIDField(
#         default=uuid.uuid4,
#         unique=True,
#         editable=False,
#         help_text="Public identifier used in this event's shareable registration link.",
#     )

#     def __str__(self):
#         return f"{self.race.name} - {self.title}"

#     def registration_path(self):
#         """Relative URL for this event's public, single-event registration page."""
#         from django.urls import reverse
#         return reverse("accounts:register_race_event", kwargs={"event_uuid": self.uuid})
    

# class RaceRegistration(models.Model):
#     # Link to the person (who holds the Bib ID)
#     participant = models.ForeignKey(
#         'accounts.Registration', 
#         on_delete=models.CASCADE,
#         related_name='race_entries'
#     )
#     # Link to the specific event (Mass Start vs Time Trial)
#     event = models.ForeignKey(
#         Event, 
#         on_delete=models.CASCADE,
#         related_name='event_registrations',
#         null=True,   # Add this
#         blank=True  # Add this
#     )
#     # Link to the overall race (for quick filtering)
#     race = models.ForeignKey(
#         Race, 
#         on_delete=models.CASCADE,
#         related_name='race_registrations'
#     )
    
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         # Prevents a user from joining the same event twice
#         unique_together = ('participant', 'event')

#     def __str__(self):
#         return f"{self.participant.name} in {self.event.title}"


# app_races/models.py
from django.db import models
from django.utils import timezone
import uuid
from django.urls import reverse

class Race(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    distance_km = models.PositiveIntegerField()
    registration_start = models.DateTimeField()
    race_start = models.DateTimeField()

    # Public, unguessable identifier used in this race's shareable,
    # type-scoped registration link: /register/race/<uuid>/type/<event_type_id>/
    uuid = models.UUIDField(
        default=uuid.uuid4,
        blank=True,
        editable=False,
        help_text="Public identifier used in this race's shareable registration links.",
    )

    def __str__(self):
        return self.name

    @property
    def status(self):
        now = timezone.now()
        if now.date() == self.race_start.date():
            return "LIVE NOW"
        elif self.registration_start <= now < self.race_start:
            return "REGISTRATION OPEN"
        return "COMING SOON"

    def registration_path_for_type(self, event_type_id):
        """
        Relative URL for this race's public registration page, scoped to
        one event type (e.g. Road Cycling vs Track Cycling). Shows a
        picker of only this race's events under that type.
        """
        return reverse(
            "accounts:register_race_by_type",
            kwargs={"race_uuid": self.uuid, "event_type_id": event_type_id},
        )

    def available_event_types(self):
        """
        Distinct DimEventType objects actually used by this race's events
        right now (via Event.category.event_type). Useful for building
        "Register for Road" / "Register for Track" links dynamically,
        e.g. on a future race detail page.
        """
        from app_admin.models import DimEventType
        return DimEventType.objects.filter(
            categories__race_events__race=self
        ).distinct()


class Event(models.Model):
    race = models.ForeignKey(
        Race,
        related_name='events',
        on_delete=models.CASCADE
    )

    category = models.ForeignKey(
        "app_admin.DimEventCategory",
        on_delete=models.PROTECT,
        related_name="race_events",
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255)
    distance_km = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True)

    # Public, unguessable identifier used in this event's shareable,
    # single-event registration link: /register/event/<uuid>/
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Public identifier used in this event's shareable registration link.",
    )

    def __str__(self):
        return f"{self.race.name} - {self.title}"

    def registration_path(self):
        """Relative URL for this event's public, single-event registration page."""
        return reverse("accounts:register_race_event", kwargs={"event_uuid": self.uuid})


class RaceRegistration(models.Model):
    # Link to the person (who holds the Bib ID)
    participant = models.ForeignKey(
        'accounts.Registration',
        on_delete=models.CASCADE,
        related_name='race_entries'
    )
    # Link to the specific event (Mass Start vs Time Trial)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_registrations',
        null=True,   # Add this
        blank=True  # Add this
    )
    # Link to the overall race (for quick filtering)
    race = models.ForeignKey(
        Race,
        on_delete=models.CASCADE,
        related_name='race_registrations'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevents a user from joining the same event twice
        unique_together = ('participant', 'event')

    def __str__(self):
        return f"{self.participant.name} in {self.event.title}"