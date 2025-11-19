from django.db import models

class TimeEntry(models.Model):
    bib_id = models.CharField(max_length=50)
    lap_time = models.DurationField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Time entry"
        verbose_name_plural = "Time entries"

    def __str__(self):
        return f"Bib {self.bib_id} — {self.lap_time}"
