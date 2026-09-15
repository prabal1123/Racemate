
from django.db import models
import uuid

class DimState(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name or ""


class DimDistrict(models.Model):
    state = models.ForeignKey(DimState, on_delete=models.CASCADE, related_name="districts")
    code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Short immutable district code for Bibs (e.g. LKO). Fill via admin/backfill."
    )
    name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        name = self.name or ""
        code = f"{self.code} " if self.code else ""
        state_name = self.state.name or ""
        return f"{code}{name} ({state_name})"


class DimGender(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name or ""


class DimEventType(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.name or ""


# class DimEventCategory(models.Model):
#     event_type = models.ForeignKey(DimEventType, on_delete=models.CASCADE, related_name="categories")
#     name = models.CharField(max_length=150, blank=True, null=True)

#     def __str__(self):
#         return f"{self.name or ''} ({self.event_type.name or ''})"

class DimEventCategory(models.Model):
    event_type = models.ForeignKey(DimEventType, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=150, blank=True, null=True)

    # Public, unguessable identifier used in shareable registration links
    # (e.g. /register/<uuid>/), instead of exposing the DB primary key.
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Public identifier used in the shareable registration link for this event.",
    )

    def __str__(self):
        return f"{self.name or ''} ({self.event_type.name or ''})"

    def registration_path(self):
        """Relative URL for this event's public, single-event registration page."""
        from django.urls import reverse
        return reverse("accounts:register", kwargs={"event_uuid": self.uuid})
    

class dimDate(models.Model):
    date = models.DateField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    day = models.IntegerField(blank=True, null=True)
    month_name = models.CharField(max_length=20, blank=True, null=True)
    day_name = models.CharField(max_length=20, blank=True, null=True)
    quarter = models.IntegerField(blank=True, null=True)
    is_weekend = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return str(self.date) if self.date is not None else ""


# New Event model used by Registration.events (ManyToMany)
class Event(models.Model):
    code = models.CharField(max_length=50, unique=True)   # e.g. 'marathon'
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["name"]

    def __str__(self):
        return self.name

