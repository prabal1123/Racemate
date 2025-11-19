# app_results/forms.py
from django import forms
from datetime import timedelta
from .models import Participation

class ParticipationForm(forms.ModelForm):
    # Present lap_time as text input where user types MM:SS
    lap_time = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "MM:SS or HH:MM:SS", "pattern": r"^\d{1,2}:\d{2}(:\d{2})?$"}),
        label="End time (MM:SS)"
    )

    class Meta:
        model = Participation
        # include the fields you want to edit via this form
        fields = ['is_participated', 'lap_time', 'total_lap_time', 'end_time']

    def clean_lap_time(self):
        raw = self.cleaned_data.get('lap_time')
        if not raw:
            return None
        raw = raw.strip()
        parts = raw.split(':')
        try:
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = int(parts[1])
                if seconds >= 60:
                    raise forms.ValidationError("Seconds must be 0–59.")
                return timedelta(minutes=minutes, seconds=seconds)
            elif len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                if minutes >= 60 or seconds >= 60:
                    raise forms.ValidationError("Minutes/seconds must be 0–59.")
                return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except ValueError:
            raise forms.ValidationError("Enter numbers only in format MM:SS or HH:MM:SS.")
        raise forms.ValidationError("Enter time as MM:SS or HH:MM:SS.")
