from django import forms
from .models import TimeEntry
import datetime


class TimeEntryForm(forms.ModelForm):
    # Accept textual lap time input (e.g. "1:23" or "01:02:03" or "83" seconds)
    lap_time_text = forms.CharField(
        label="Lap time (MM:SS or HH:MM:SS or seconds)",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "MM:SS or HH:MM:SS or seconds"})
    )

    class Meta:
        model = TimeEntry
        fields = ['bib_id', 'note']  # lap_time will be filled from lap_time_text

    def clean_lap_time_text(self):
        s = self.cleaned_data['lap_time_text'].strip()
        # If purely digits, treat as seconds
        parts = s.split(':')
        try:
            if len(parts) == 1:
                # seconds
                seconds = float(parts[0])
                td = datetime.timedelta(seconds=seconds)
            elif len(parts) == 2:
                # MM:SS
                minutes = int(parts[0])
                seconds = float(parts[1])
                td = datetime.timedelta(minutes=minutes, seconds=seconds)
            elif len(parts) == 3:
                # HH:MM:SS
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                td = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
            else:
                raise ValueError("Bad format")
        except Exception:
            raise forms.ValidationError("Enter time as seconds or MM:SS or HH:MM:SS (e.g. 1:23 or 01:02:03 or 83)")
        return td

    def save(self, commit=True):
        instance = super().save(commit=False)
        # lap_time_text was cleaned to a timedelta
        instance.lap_time = self.cleaned_data['lap_time_text']
        if commit:
            instance.save()
        return instance
