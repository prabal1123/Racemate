from django.db import models
import datetime

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


def release_bib(self):
    """
    Logic to generate and save a BIB ID.
    Format: [DistrictCode]-[Category]-[Gender]-[Year]-[Serial]
    """
    if self.bib_id:
        return self.bib_id

    # 1. Get District Code (fallback to 'GEN' if missing)
    district_code = "GEN"
    if self.district_fk and hasattr(self.district_fk, 'code'):
        district_code = self.district_fk.code
    elif hasattr(self, 'district') and self.district:
        district_code = str(self.district)[:3].upper()

    # 2. Get Year
    year = datetime.date.today().year

    # 3. Get Serial (Count of existing bibs + 1)
    from accounts.models import Registration
    count = Registration.objects.filter(bib_id__icontains=str(year)).count() + 1
    serial = f"{count:04d}" 

    # 4. Construct ID (e.g., LKW-SEN-M-2026-0011)
    gender_code = (self.gender[0].upper() if self.gender else "X")
    cat_code = (self.category[:3].upper() if self.category else "RUN")
    
    new_id = f"{district_code}-{cat_code}-{gender_code}-{year}-{serial}"
    
    self.bib_id = new_id
    self.bib_released_at = datetime.datetime.now()
    self.save()
    return new_id