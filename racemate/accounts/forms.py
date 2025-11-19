
# accounts/forms.py
from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Registration
from app_admin.models import DimState, DimDistrict, DimEventCategory


class RegistrationForm(forms.ModelForm):
    state = forms.ModelChoiceField(
        queryset=DimState.objects.all().order_by('name'),
        required=False,
        empty_label="Select state"
    )

    district_fk = forms.ModelChoiceField(
        queryset=DimDistrict.objects.none(),
        required=False,
        label="District (select)"
    )

    # ManyToMany on Registration -> use ModelMultipleChoiceField
    events = forms.ModelMultipleChoiceField(
        queryset=DimEventCategory.objects.all().order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Events Category"
    )

    class Meta:
        model = Registration
        fields = [
        'name', 'fathers_name', 'date_of_birth', 'gender' ,'profession',
        'address', 'representing_from', 'mobile_number', 'aadhar_number',
        'events', 'state', 'district_fk',
        ]

        widgets = {
            # Keep as plain text input so flatpickr can attach reliably
            'date_of_birth': forms.TextInput(attrs={
                'id': 'id_date_of_birth',
                'placeholder': 'YYYY-MM-DD',
                'class': 'form-input',
                'autocomplete': 'off',
            }),
        }

    def __init__(self, *args, **kwargs):
        initial_state_id = kwargs.pop('initial_state_id', None)
        super().__init__(*args, **kwargs)

        # Populate districts depending on state (POST / instance / initial)
        if self.data.get('state'):
            try:
                state_id = int(self.data.get('state'))
                self.fields['district_fk'].queryset = DimDistrict.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['district_fk'].queryset = DimDistrict.objects.none()
        elif self.instance and getattr(self.instance, 'district_fk', None):
            self.fields['district_fk'].queryset = DimDistrict.objects.filter(state=self.instance.state).order_by('name')
        elif initial_state_id:
            self.fields['district_fk'].queryset = DimDistrict.objects.filter(state_id=initial_state_id).order_by('name')
        else:
            self.fields['district_fk'].queryset = DimDistrict.objects.none()

        # Refresh events queryset (useful if you add event categories from admin while dev server is running)
        self.fields['events'].queryset = DimEventCategory.objects.all().order_by('name')

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            # dob should be a date object (ModelForm typically converts); ensure not future
            try:
                if hasattr(dob, 'year'):
                    dob_date = dob
                else:
                    raise ValueError("Invalid date")
                if dob_date > timezone.localdate():
                    raise ValidationError("Date of birth cannot be in the future.")
            except (ValueError, TypeError):
                raise ValidationError("Enter a valid date of birth.")
        return dob

    def clean(self):
        cleaned = super().clean()
        state = cleaned.get('state')
        district = cleaned.get('district_fk')
        if state and district and district.state_id != state.id:
            raise forms.ValidationError("Selected district doesn't belong to selected state.")
        return cleaned
