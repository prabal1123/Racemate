
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

import random
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

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

# class Registration(models.Model):
#     PROFESSION_CHOICES = [
#         ('student', 'Student'),
#         ('employee', 'Employee'),
#         ('business', 'Business'),
#     ]
#     GENDER_CHOICES = [
#         ('male', 'Male'),
#         ('female', 'Female'),
#         ('other', 'Other'),
#     ]

#     # --- New Core Relationship ---
#     race = models.ForeignKey(
#         "app_races.Race",
#         on_delete=models.PROTECT,
#        related_name="account_registrations",
#        null=True, # Temporary
#         blank=True,
#         verbose_name=_("Selected Race"),
#         help_text=_("The specific race event the user is registering for.")
#     )

#     # --- Personal Details ---
#     name = models.CharField(_("Full name"), max_length=200)
#     fathers_name = models.CharField(_("Father's name"), max_length=200, blank=True)
#     date_of_birth = models.DateField(_("Date of birth"), null=True, blank=True)
#     gender = models.CharField(_("Gender"), max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
#     profession = models.CharField(_("Profession"), max_length=20, choices=PROFESSION_CHOICES, blank=True)
#     address = models.TextField(_("Address"), blank=True)

#     # --- Location Logic ---
#     state = models.ForeignKey(
#         DimState,
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True,
#         related_name="registrations",
#         verbose_name=_("State")
#     )
#     district_fk = models.ForeignKey(
#         DimDistrict,
#         on_delete=models.PROTECT,
#         null=True,
#         blank=True,
#         related_name="registrations_fk",
#         verbose_name=_("District")
#     )
#     representing_from = models.CharField(_("Representing from"), max_length=200, blank=True)

#     # --- Contact & Identity ---
#     mobile_number = models.CharField(
#         _("Mobile number"),
#         max_length=20,
#         blank=True,
#         validators=[phone_validator]
#     )
#     aadhar_number = models.CharField(
#         _("Aadhaar"),
#         max_length=12,
#         blank=True,
#         validators=[aadhar_validator]
#     )
#     email = models.EmailField(_("Email"), max_length=254, blank=True, null=True)

#     # --- Metadata & Bibs ---
#     created_at = models.DateTimeField(auto_now_add=True)
#     category = models.CharField(_("Assigned category"), max_length=255, null=True, blank=True)
#     bib_id = models.CharField(_("Bib ID"), max_length=50, unique=True, null=True, blank=True)
#     bib_released_at = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = _("Registration")
#         verbose_name_plural = _("Registrations")
#         indexes = [
#             models.Index(fields=['mobile_number'], name='reg_mobile_idx'),
#             models.Index(fields=['aadhar_number'], name='reg_aadhar_idx'),
#         ]

#     def __str__(self):
#         race_name = self.race.name if self.race else "No Race"
#         return f"{self.name} — {race_name} — {self.mobile_number or 'no-phone'}"

#     def clean(self):
#         if self.aadhar_number:
#             if not self.aadhar_number.isdigit() or len(self.aadhar_number) != 12:
#                 raise ValidationError({'aadhar_number': _("Aadhaar must be 12 digits.")})
#         if self.state and self.district_fk:
#             if self.district_fk.state_id != self.state.id:
#                 raise ValidationError(_("Selected district does not belong to selected state."))

#     # -------------------
#     # Age / Category Logic
#     # -------------------
#     def age_on(self, on_date=None):
#         if not self.date_of_birth: return None
#         if on_date is None: on_date = date.today()
#         years = on_date.year - self.date_of_birth.year
#         if (on_date.month, on_date.day) < (self.date_of_birth.month, self.date_of_birth.day):
#             years -= 1
#         return years

#     def assign_category(self, event_date=None):
#         if event_date is None:
#             # Try to get date from the associated Race instance
#             event_date = self.race.race_start.date() if self.race else date.today()

#         age = self.age_on(event_date)
#         if age is None: return "Unspecified"
        
#         if age >= 56: return "Masters Men 56+"
#         if 46 <= age <= 55: return "Masters Men 46 to 55 years"
#         if 36 <= age <= 45: return "Masters Men 36 to 45 years"
#         if 12 <= age <= 14: return "Youth Boys & Youth Girls (12-14)"
#         if 15 <= age <= 16: return "Sub-Junior Boys & Sub-Junior Girls (15 & 16)"
#         if 17 <= age <= 18: return "Junior Boys & Junior Girls (17 & 18)"
#         if 19 <= age <= 22: return "Men under-23 (19-22)"
#         if age >= 19: return "Men Elite & Women Elite (19 & above)"
#         return "Other / Not categorized"

#     def save(self, *args, **kwargs):
#         try:
#             self.category = self.assign_category()
#         except Exception:
#             pass
#         super().save(*args, **kwargs)

#     # -------------------
#     # Updated Bib Format
#     # -------------------
#     def _format_bib(self, seq_num: int):
#         """
#         Build: [RACE_SLUG]-[DIST_CODE]-[GENDER]-[YEAR]-[SEQ]
#         Example: CTCC-BHO-M-2026-0001
#         """
#         # 1. Race Prefix (First 4 letters of name)
#         race_prefix = slugify(self.race.name)[:4].upper() if self.race else "RACE"
        
#         # 2. District Code
#         if self.district_fk and self.district_fk.code:
#             dist = self.district_fk.code.upper()
#         else:
#             dist = "UNK"

#         # 3. Short Category/Gender info
#         gender = (self.gender or "O")[0].upper()
        
#         # 4. Sequential Number
#         regno = f"{seq_num:04d}"
        
#         # 5. Year (from race start or creation)
#         year = self.race.race_start.year if self.race else timezone.now().year

#         return f"{race_prefix}-{dist}-{gender}-{year}-{regno}"
 

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.text import slugify
from datetime import date

# Import location models directly to avoid loading errors
from app_admin.models import DimState, DimDistrict

# --- Validators ---
phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message=_("Enter a valid phone number (7-15 digits, optional leading +).")
)

aadhar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message=_("Aadhaar must be exactly 12 digits.")
)

# --- Sequence Models ---

class GlobalSequence(models.Model):
    """
    A simple global counter used for IDs and Bib numbers.
    """
    name = models.CharField(max_length=100, unique=True)
    seq = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name}:{self.seq}"


# --- Main Registration Model ---

class Registration(models.Model):

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    # --- Core Relationship ---
    race = models.ForeignKey(
        "app_races.Race",
        on_delete=models.PROTECT,
        related_name="account_registrations",
        null=True, 
        blank=True,
        verbose_name=_("Selected Race")
    )

    # Simple field to store heat as a number (Replaces old Heat Model)
    heat_number = models.IntegerField(
        _("Heat Number"),
        null=True,
        blank=True,
        help_text=_("The group/wave number assigned based on DOB.")
    )

    # --- Personal Details ---
    name = models.CharField(_("Full name"), max_length=200)
    fathers_name = models.CharField(_("Father's name"), max_length=200, blank=True)
    date_of_birth = models.DateField(_("Date of birth"), null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    school_name = models.CharField(_("School / College / Club"), max_length=200, blank=True)
    address = models.TextField(_("Address"), blank=True)

    # --- Location Logic ---
    state = models.ForeignKey(
        DimState, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name="registrations"
    )
    district_fk = models.ForeignKey(
        DimDistrict, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name="registrations_fk"
    )
    representing_from = models.CharField(_("Representing from"), max_length=200, blank=True)

    # --- Contact & Identity ---
    mobile_number = models.CharField(
        _("Mobile number"), 
        max_length=20, 
        blank=True, 
        validators=[phone_validator]
    )
    aadhar_number = models.CharField(
        _("Aadhaar"), 
        max_length=12, 
        blank=True, 
        validators=[aadhar_validator]
    )
    email = models.EmailField(_("Email"), max_length=254, blank=True, null=True)

    # --- Metadata & ID Generation ---
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(_("Assigned category"), max_length=255, null=True, blank=True)
    
    registration_id = models.CharField(
        _("Registration ID"), 
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True, 
        editable=False
    )
    
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
        return f"{self.name} — {self.registration_id or 'No ID'}"

    # --- Logic ---

    def age_on(self, on_date=None):
        if not self.date_of_birth: 
            return None
        if on_date is None: 
            on_date = date.today()
        years = on_date.year - self.date_of_birth.year
        if (on_date.month, on_date.day) < (self.date_of_birth.month, self.date_of_birth.day):
            years -= 1
        return years
    
    def get_race_initials(self):
        if self.race and self.race.name:
            words = self.race.name.split()
            return "".join([word[0].upper() for word in words if word])[:4]
        return "REG"

    def assign_category(self, event_date=None):
        if event_date is None:
            if self.race and self.race.race_start:
                event_date = self.race.race_start.date()
            else:
                event_date = date.today()
        
        age = self.age_on(event_date)
        if age is None: return "Unspecified"
        
        if age >= 56: return "Masters Men 56+"
        if 46 <= age <= 55: return "Masters Men 46 to 55 years"
        if 36 <= age <= 45: return "Masters Men 36 to 45 years"
        if 19 <= age <= 22: return "Men under-23 (19-22)"
        if age >= 19: return "Men Elite & Women Elite (19 & above)"
        return "Junior Categories"

    def save(self, *args, **kwargs):
        # 1. Category Auto-Assignment
        if not self.category:
            try:
                self.category = self.assign_category()
            except:
                pass

        # 2. Registration ID Generation (e.g., CTCC-0001)
        if not self.registration_id:
            prefix = self.get_race_initials()
            with transaction.atomic():
                seq_row, _ = GlobalSequence.objects.select_for_update().get_or_create(
                    name=f"reg_seq_{prefix}",
                    defaults={'seq': 0}
                )
                seq_row.seq += 1
                seq_row.save()
                self.registration_id = f"{prefix}-{seq_row.seq:04d}"

        super().save(*args, **kwargs)

    def release_bib(self):
        """
        Generates the District-based Bib ID.
        """
        if self.bib_id:
            return self.bib_id

        prefix = self.get_race_initials()
        
        dist_code = self.district_fk.code.upper() if (self.district_fk and self.district_fk.code) else "UNK"
        gender = (self.gender or "O")[0].upper()
        year = self.race.race_start.year if (self.race and self.race.race_start) else date.today().year

        with transaction.atomic():
            seq_key = f"bib_seq_{prefix}_{dist_code}"
            seq_row, _ = GlobalSequence.objects.select_for_update().get_or_create(
                name=seq_key,
                defaults={'seq': 0}
            )
            seq_row.seq += 1
            seq_row.save()
            
            self.bib_id = f"{prefix}-{dist_code}-{gender}-{year}-{seq_row.seq:04d}"
            self.bib_released_at = timezone.now()
            self.save()
            
        return self.bib_id


class EmailOTP(models.Model):
    email = models.EmailField()

    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 300  # 5 min



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_image = models.ImageField(upload_to='profile_pics/', default='default.jpg', blank=True)
    dob = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    
    # Identity & Address for "View More" section
    pan_number = models.CharField(max_length=10, blank=True)
    aadhaar_number = models.CharField(max_length=12, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=6, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    

