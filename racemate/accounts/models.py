
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from app_admin.models import DimState, DimDistrict

from datetime import date
from django.conf import settings

# new imports for bib generation
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.text import slugify
from django.db import IntegrityError

phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message=_("Enter a valid phone number (7-15 digits, optional leading +).")
)

aadhar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message=_("Aadhaar must be exactly 12 digits.")
)


class RegistrationSequence(models.Model):
    """
    Keeps per-(district,year,age_category,gender) sequence to safely generate bib numbers.
    (Kept for backward compatibility / other uses; not used for global seq)
    """
    district = models.ForeignKey(DimDistrict, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    age_category = models.CharField(max_length=32)   # short category like 'U18','U23','SEN'
    gender = models.CharField(max_length=10)         # 'male','female','other'
    seq = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('district', 'year', 'age_category', 'gender')
        indexes = [
            models.Index(fields=['district', 'year', 'age_category', 'gender'], name='seq_idx'),
        ]

    def __str__(self):
        return f"{self.district_id}-{self.year}-{self.age_category}-{self.gender}:{self.seq}"


class GlobalSequence(models.Model):
    """
    A simple global counter used for trailing bib number (0001,0002,...).
    """
    name = models.CharField(max_length=100, unique=True)  # use 'registration' as name
    seq = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name}:{self.seq}"


class Registration(models.Model):
    PROFESSION_CHOICES = [
        ('student', 'Student'),
        ('employee', 'Employee'),
        ('business', 'Business'),
    ]

    name = models.CharField(_("Full name"), max_length=200)
    fathers_name = models.CharField(_("Father's name"), max_length=200, blank=True)
    date_of_birth = models.DateField(_("Date of birth"), null=True, blank=True)
    profession = models.CharField(_("Profession"), max_length=20, choices=PROFESSION_CHOICES, blank=True)
    address = models.TextField(_("Address"), blank=True)

    # Legacy free-text district (kept for migration/backwards compatibility)
    district = models.CharField(
        _("District (legacy)"),
        max_length=200,
        blank=True,
        help_text=_("Legacy/free-text district field; used for migration.")
    )
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    gender = models.CharField(
        _("Gender"),
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )

    # Foreign Keys
    state = models.ForeignKey(
        DimState,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="registrations",
        verbose_name=_("State"),
        help_text=_("Selected state (FK to DimState).")
    )
    district_fk = models.ForeignKey(
        DimDistrict,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="registrations_fk",
        verbose_name=_("District"),
        help_text=_("Selected district (FK to DimDistrict).")
    )

    representing_from = models.CharField(_("Representing from"), max_length=200, blank=True)
    mobile_number = models.CharField(
        _("Mobile number"),
        max_length=20,
        blank=True,
        validators=[phone_validator],
        help_text=_("Include country code if applicable, e.g. +91XXXXXXXXXX")
    )
    aadhar_number = models.CharField(
        _("Aadhaar"),
        max_length=12,
        blank=True,
        validators=[aadhar_validator],
        help_text=_("12 digit Aadhaar number without spaces.")
    )

    # Email (added because code references it)
    email = models.EmailField(_("Email"), max_length=254, blank=True, null=True)

    # Many-to-Many relation to Event model
    events = models.ManyToManyField(
        "app_admin.DimEventCategory",
        blank=True,
        related_name="registrations",
        verbose_name=_("Events"),
        help_text=_("Events the registrant is participating in.")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # store computed category (nullable so migration is easy)
    category = models.CharField(_("Assigned category"), max_length=255, null=True, blank=True,
                                help_text=_("Computed competition category for registrant (auto-calculated)."))

    # --- NEW fields for Bibs ---
    bib_id = models.CharField(_("Bib ID"), max_length=50, unique=True, null=True, blank=True)
    bib_released_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Registration")
        verbose_name_plural = _("Registrations")
        indexes = [
            models.Index(fields=['mobile_number'], name='reg_mobile_idx'),
            models.Index(fields=['aadhar_number'], name='reg_aadhar_idx'),
        ]

    def __str__(self):
        return f"{self.name} — {self.mobile_number or 'no-phone'}"

    def clean(self):
        # Ensure aadhar is exactly 12 digits if provided
        if self.aadhar_number:
            if not self.aadhar_number.isdigit() or len(self.aadhar_number) != 12:
                raise ValidationError({'aadhar_number': _("Aadhaar must be 12 digits.")})

        # State / District consistency
        if self.state and self.district_fk:
            if self.district_fk.state_id != self.state.id:
                raise ValidationError(_("Selected district does not belong to selected state."))

        # Optional: auto-set state from district if state missing but district provided
        if not self.state and self.district_fk:
            self.state = self.district_fk.state

    # -------------------
    # Age / category helpers
    # -------------------
    def age_on(self, on_date=None):
        """
        Compute integer age in years on `on_date` (defaults to today).
        Returns None if date_of_birth not set.
        """
        if not self.date_of_birth:
            return None
        if on_date is None:
            on_date = date.today()
        years = on_date.year - self.date_of_birth.year
        if (on_date.month, on_date.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years

    def birth_year(self):
        return self.date_of_birth.year if self.date_of_birth else None

    def assign_category(self, event_date=None):
        """
        Decide a category string based on age (on event date).
        Adjust the ranges to match your official rulebook.
        """
        if event_date is None:
            event_date = getattr(settings, "EVENT_DATE", date.today())

        age = self.age_on(event_date)
        if age is None:
            return "Unspecified"

        # ----- DEFAULT MAPPING (edit to fit exact rules) -----
        if age >= 56:
            return "Masters Men 56+"
        if 46 <= age <= 55:
            return "Masters Men 46 to 55 years"
        if 36 <= age <= 45:
            return "Masters Men 36 to 45 years"
        if 12 <= age <= 14:
            return "Youth Boys & Youth Girls (12-14)"
        if 15 <= age <= 16:
            return "Sub-Junior Boys & Sub-Junior Girls (15 & 16)"
        if 17 <= age <= 18:
            return "Junior Boys & Junior Girls (17 & 18)"
        # Under-23 placeholder range; adjust if using birth-year bands
        if 19 <= age <= 22:
            return "Men under-23 (19-22)"
        if age >= 19:
            return "Men Elite & Women Elite (19 & above)"
        return "Other / Not categorized"

    def save(self, *args, **kwargs):
        # compute category before saving (uses EVENT_DATE from settings by default)
        try:
            self.category = self.assign_category()
        except Exception:
            # do not block save for category computation failures
            self.category = self.category or None
        super().save(*args, **kwargs)

    # -------------------
    # Bib helpers & generator
    # -------------------
    def short_age_category(self):
        """
        Return a short age category token used in the bib (adjust mapping as needed).
        Defaults: U18, U23, SEN (for 23-55), M56 (56+).
        """
        age = self.age_on(getattr(settings, "EVENT_DATE", None) or date.today())
        if age is None:
            # fallback: try to parse numeric from self.category
            if self.category:
                # crude attempt: pick first number in category if present
                import re
                m = re.search(r'(\d{2})', self.category)
                if m:
                    val = int(m.group(1))
                    if val <= 18:
                        return f"U{val}"
                # otherwise shorten text
                return (self.category.split()[0] or "GEN")[:10].upper()
            return "GEN"
        if age <= 18:
            return "U18"
        if 19 <= age <= 22:
            return "U23"
        if age >= 56:
            return "M56"
        # 23-55
        return "SEN"

    def _format_bib(self, seq_num: int):
        """
        Build: [DIST]-[AgeCategory]-[GENDER]-[Year]-[0001]
        """
        # DIST: prefer code, else slugified short name
        if self.district_fk and self.district_fk.code:
            dist = self.district_fk.code.upper()
        elif self.district_fk and self.district_fk.name:
            dist = slugify(self.district_fk.name)[:3].upper() or "UNK"
        else:
            dist = "UNK"

        age_cat = self.short_age_category()
        gender = (self.gender or "other")[0].upper()  # male->M, female->F, other->O
        year = (self.created_at.year if self.created_at else timezone.now().year)
        regno = f"{seq_num:04d}"
        return f"{dist}-{age_cat}-{gender}-{year}-{regno}"

    def release_bib(self, notify=False, max_retries: int = 3):
        """
        Atomically assign a bib_id if not already assigned.
        Uses GlobalSequence for a global trailing counter (0001,0002,...).
        Returns the bib_id.
        """
        if self.bib_id:
            return self.bib_id

        district = self.district_fk
        if district is None:
            raise ValueError("Cannot release bib: registration has no district_fk set.")

        # Use global sequence name "registration"
        for attempt in range(1, max_retries + 1):
            try:
                with transaction.atomic():
                    seq_row, created = GlobalSequence.objects.select_for_update().get_or_create(
                        name='registration', defaults={'seq': 0}
                    )
                    seq_row.seq = F('seq') + 1
                    seq_row.save()
                    seq_row.refresh_from_db(fields=['seq'])
                    seq = seq_row.seq

                    if seq > 9999:
                        raise ValueError("Sequence overflow for bucket: consider expanding regno digits or changing scope.")

                    # assign and save bib fields (defensive save)
                    self.bib_id = self._format_bib(seq)
                    self.bib_released_at = timezone.now()
                    try:
                        self.save(update_fields=['bib_id', 'bib_released_at'])
                    except IntegrityError:
                        # If bib_id unique constraint failed (very rare), raise to outer retry
                        raise

                # schedule notifications after commit (non-blocking wrt transaction)
                if notify and getattr(self, 'email', None):
                    def _send():
                        try:
                            send_mail(
                                subject="Your Bib ID",
                                message=f"Hello {self.name},\n\nYour Bib ID is: {self.bib_id}\n\nPlease save it.",
                                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                                recipient_list=[self.email],
                                fail_silently=True
                            )
                        except Exception:
                            pass
                    transaction.on_commit(_send)

                return self.bib_id

            except IntegrityError:
                # possible race on unique bib_id; retry a few times
                if attempt >= max_retries:
                    raise
                # else loop to retry
            except Exception:
                # other exceptions: re-raise (you can customize handling)
                raise

        # if loop falls through (shouldn't), raise
        raise RuntimeError("Failed to generate bib after retries.")
