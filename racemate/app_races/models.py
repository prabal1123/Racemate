
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
#     title = models.CharField(max_length=255) # "Mass Start", "Time Trial", etc.
#     # You can add event-specific distances or fees here
    
#     def __str__(self):
#         return f"{self.race.name} - {self.title}"


# app_races/models.py

class Event(models.Model):
    race = models.ForeignKey(Race, related_name='events', on_delete=models.CASCADE)
    title = models.CharField(max_length=255) 
    distance_km = models.PositiveIntegerField(null=True, blank=True) # Must be here
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Must be here
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.race.name} - {self.title}"
    

# class RaceRegistration(models.Model):
#     race = models.ForeignKey(Race, related_name='registrations', on_delete=models.CASCADE)
    
#     participant = models.ForeignKey(
#         'accounts.Registration', 
#         on_delete=models.CASCADE,
#         related_name='race_entries',
#         null=True,
#         blank=True
#     )
    
#     # REMOVED: heat = models.ForeignKey(Heat, ...) <- DELETE THIS LINE
    
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         participant_name = self.participant.name if self.participant else "Unknown"
#         return f"{participant_name} registered for {self.race.name}"

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