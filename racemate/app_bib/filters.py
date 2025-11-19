
# /filters.py
import django_filters
from django import forms
from datetime import date
from django.core.exceptions import FieldDoesNotExist

from accounts.models import Registration


class RegistrationFilter(django_filters.FilterSet):
    """
    Filters for Bib List Page.
    Supports: district, gender, age group.

    This implementation discovers the model used for `district_fk` at runtime
    (so we don't need to import District directly and won't crash if it lives
    in another app).
    """
    AGE_GROUP_CHOICES = [
        ('under18', 'Under 18'),
        ('18to29', '18–29'),
        ('30to45', '30–45'),
        ('46to55', '46–55'),
        ('56plus', '56+'),
    ]

    # We'll initialize district queryset in __init__ below to avoid importing District statically.
    district_fk = django_filters.ModelChoiceFilter(
        queryset=Registration.objects.none(),
        label='District',
        field_name='district_fk',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    gender = django_filters.ChoiceFilter(
        field_name='gender',
        choices=getattr(Registration, 'GENDER_CHOICES', ()),
        label='Gender',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    age_group = django_filters.ChoiceFilter(
        label='Age Group',
        choices=AGE_GROUP_CHOICES,
        method='filter_age_group',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Registration
        fields = ['district_fk', 'gender', 'age_group']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Attempt to find the model referenced by the 'district_fk' field on Registration.
        # This avoids a hard import such as `from locations.models import District`.
        try:
            field = Registration._meta.get_field('district_fk')
            related_model = getattr(field, 'remote_field', None)
            if related_model:
                DistrictModel = field.remote_field.model
                try:
                    qs = DistrictModel.objects.order_by('name')
                except Exception:
                    qs = DistrictModel.objects.all()
                # assign the queryset to the filter so the <select> is populated
                self.filters['district_fk'].queryset = qs
        except FieldDoesNotExist:
            # If the field isn't present, leave the queryset as empty to avoid crashing.
            # Template will still render a disabled/empty select unless you handle it there.
            self.filters['district_fk'].queryset = Registration.objects.none()
        except Exception:
            # Any other error (safety net): leave the queryset empty but don't crash.
            self.filters['district_fk'].queryset = Registration.objects.none()

    def _safe_date(self, year, month, day):
        """Return a valid date for year/month/day; fallback to day=1 if invalid (Feb 29 handling)."""
        try:
            return date(year, month, day)
        except ValueError:
            return date(year, month, 1)

    def filter_age_group(self, queryset, name, value):
        """
        Filter registrations by age group using date_of_birth ranges.
        Excludes registrations with null date_of_birth.
        """
        today = date.today()

        def years_ago(n):
            return self._safe_date(today.year - n, today.month, today.day)

        qs = queryset.filter(date_of_birth__isnull=False)

        if value == 'under18':
            cutoff = years_ago(18)
            return qs.filter(date_of_birth__gt=cutoff)

        if value == '18to29':
            upper = years_ago(18)
            lower = years_ago(29)
            return qs.filter(date_of_birth__range=(lower, upper))

        if value == '30to45':
            upper = years_ago(30)
            lower = years_ago(45)
            return qs.filter(date_of_birth__range=(lower, upper))

        if value == '46to55':
            upper = years_ago(46)
            lower = years_ago(55)
            return qs.filter(date_of_birth__range=(lower, upper))

        if value == '56plus':
            cutoff = years_ago(56)
            return qs.filter(date_of_birth__lte=cutoff)

        return queryset
