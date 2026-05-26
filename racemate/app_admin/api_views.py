from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
# Explicitly import JWTAuthentication for Postman/Bearer support
from rest_framework_simplejwt.authentication import JWTAuthentication 
from django.db.models import Count
from django.db.models.functions import TruncDate
from accounts.models import Registration

class AdminDashboardAnalyticsAPI(APIView):
    """
    Returns data for the React charts: Total users, 
    registrations by state, gender, and daily trends.
    """
    # This line is crucial for Postman to recognize your Bearer token
    authentication_classes = [JWTAuthentication]
    # This ensures only users with is_staff=True can access it
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Registration.objects.all()

        # Daily Trend (Registration growth over time)
        series = qs.annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id')).order_by('day')
        
        # Breakdown by State
        by_state = qs.values('state__name').annotate(count=Count('id')).order_by('-count')

        # Breakdown by Gender
        by_gender = qs.values('gender').annotate(count=Count('id'))

        return Response({
            'total_registrations': qs.count(),
            'daily_series': list(series),
            'by_state': list(by_state),
            'by_gender': list(by_gender),
        })