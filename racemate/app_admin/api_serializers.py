from rest_framework import serializers
from accounts.models import Registration
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'code', 'name']

class AdminRegistrationSerializer(serializers.ModelSerializer):
    events = EventSerializer(many=True, read_only=True)
    district_name = serializers.CharField(source='district_fk.name', read_only=True)
    
    class Meta:
        model = Registration
        fields = [
            'id', 'registration_id', 'name', 'bib_id', 
            'gender', 'mobile_number', 'district_name', 
            'events', 'category', 'is_paid'
        ]