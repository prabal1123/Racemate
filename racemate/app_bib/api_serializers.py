from rest_framework import serializers
from accounts.models import Registration
from .models import TimeEntry

class BibRegistrationSerializer(serializers.ModelSerializer):
    # These match the logic in your current views.py
    bib_public = serializers.SerializerMethodField()
    age_display = serializers.SerializerMethodField()
    district_name = serializers.CharField(source='district_fk.name', read_only=True)

    class Meta:
        model = Registration
        fields = [
            'id', 'registration_id', 'name', 'bib_id', 
            'bib_public', 'age_display', 'gender', 
            'district_name', 'is_paid'
        ]

    def get_bib_public(self, obj):
        if not obj.bib_id: return "—"
        # Reusing your regex logic: remove the year segment
        import re
        parts = str(obj.bib_id).split('-')
        for i, p in enumerate(parts):
            if re.fullmatch(r'\d{4}', p):
                parts.pop(i)
                return '-'.join(parts)
        return str(obj.bib_id)

    def get_age_display(self, obj):
        from datetime import date
        dob = getattr(obj, 'date_of_birth', None)
        if not dob: return "—"
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return str(age)

class TimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeEntry
        fields = ['id', 'bib_id', 'lap_time', 'note', 'created_at']