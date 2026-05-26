from rest_framework import serializers
from .models import Race

class RaceSerializer(serializers.ModelSerializer):
    # This automatically counts the registrations linked to the race
    rider_count = serializers.IntegerField(source='registrations.count', read_only=True)
    # This pulls the @property logic we wrote in the model
    status_label = serializers.ReadOnlyField(source='status')

    class Meta:
        model = Race
        fields = [
            'id', 
            'name', 
            'location', 
            'distance_km', 
            'race_start', 
            'registration_start', 
            'rider_count', 
            'status_label'
        ]