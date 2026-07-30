from django import forms

from .models import MatchSet
from django.forms import inlineformset_factory
from .models import TournamentEntry
from .models import Tournament, TournamentCategory

class MatchSetScoreForm(forms.ModelForm):
    """
    Form used by the admin-only score entry page.

    The MatchSet model itself handles:

    - Score validation
    - Set winner calculation
    - Overall match winner calculation
    - Match completion
    - Winner advancement
    """

    class Meta:
        model = MatchSet

        fields = (
            "set_number",
            "entry_one_score",
            "entry_two_score",
            "is_completed",
        )

        widgets = {
            "set_number": forms.HiddenInput(),

            "entry_one_score": forms.NumberInput(
                attrs={
                    "min": 0,
                    "class": "vIntegerField",
                }
            ),

            "entry_two_score": forms.NumberInput(
                attrs={
                    "min": 0,
                    "class": "vIntegerField",
                }
            ),

            "is_completed": forms.CheckboxInput(),
        }

        labels = {
            "entry_one_score": "Entry one score",
            "entry_two_score": "Entry two score",
            "is_completed": "Set completed",
        }

    def clean(self):
        cleaned_data = super().clean()

        is_completed = cleaned_data.get(
            "is_completed"
        )

        score_one = cleaned_data.get(
            "entry_one_score"
        )

        score_two = cleaned_data.get(
            "entry_two_score"
        )

        if (
            is_completed
            and score_one is not None
            and score_two is not None
            and score_one == score_two
        ):
            raise forms.ValidationError(
                "A completed set cannot have equal scores."
            )

        return cleaned_data



class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = (
            "name",
            "sport",
            "venue",
            "registration_start",
            "registration_end",
            "tournament_start",
            "tournament_end",
            "description",
        )
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "sport": forms.Select(attrs={"class": "form-select"}),
            "venue": forms.TextInput(attrs={"class": "form-control"}),
            "registration_start": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "registration_end": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "tournament_start": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "tournament_end": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Prefill datetime-local inputs correctly when editing.
        for field_name in (
            "registration_start",
            "registration_end",
            "tournament_start",
            "tournament_end",
        ):
            value = getattr(self.instance, field_name, None)
            if value:
                self.initial[field_name] = value.strftime("%Y-%m-%dT%H:%M")


class TournamentCategoryForm(forms.ModelForm):
    class Meta:
        model = TournamentCategory
        fields = (
            "category",
            "entry_format",
            "fixture_type",
            "scoring_rule",
            "entry_fee",
            "maximum_entries",
            "registration_open",
            "is_active",
        )
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "entry_format": forms.Select(attrs={"class": "form-select"}),
            "fixture_type": forms.Select(attrs={"class": "form-select"}),
            "scoring_rule": forms.Select(attrs={"class": "form-select"}),
            "entry_fee": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "maximum_entries": forms.NumberInput(attrs={"class": "form-control"}),
            "registration_open": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


TournamentCategoryFormSet = inlineformset_factory(
    Tournament,
    TournamentCategory,
    form=TournamentCategoryForm,
    extra=1,
    can_delete=True,
)



class TournamentEntryForm(forms.ModelForm):
    class Meta:
        model = TournamentEntry
        fields = ("status", "seed", "display_name")
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "seed": forms.NumberInput(attrs={"class": "form-control"}),
            "display_name": forms.TextInput(attrs={"class": "form-control"}),
        }


