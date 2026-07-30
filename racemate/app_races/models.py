
# app_races/models.py
from django.db import models
from django.utils import timezone

class Race(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    distance_km = models.PositiveIntegerField()
    registration_start = models.DateTimeField()
    race_start = models.DateTimeField()

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


# class Event(models.Model):
#     race = models.ForeignKey(Race, related_name='events', on_delete=models.CASCADE)
#     title = models.CharField(max_length=255) 
#     distance_km = models.PositiveIntegerField(null=True, blank=True) # Must be here
#     price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Must be here
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return f"{self.race.name} - {self.title}"
    

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

    def __str__(self):
        return f"{self.race.name} - {self.title}"


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

# class DoublesEntry(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     player_one = models.ForeignKey(
#         "accounts.Registration",
#         on_delete=models.CASCADE,
#         related_name="doubles_entries_as_player_one"
#     )
#     player_two = models.ForeignKey(
#         "accounts.Registration",
#         on_delete=models.CASCADE,
#         related_name="doubles_entries_as_player_two"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)