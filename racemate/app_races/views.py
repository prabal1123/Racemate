from rest_framework import generics
from .models import Race
from .serializers import RaceSerializer

class RaceListView(generics.ListAPIView):
    queryset = Race.objects.all().order_by('race_start')
    serializer_class = RaceSerializer