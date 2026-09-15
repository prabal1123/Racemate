from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from accounts.models import Registration
from .models import TimeEntry
from .api_serializers import TimeEntrySerializer

class BulkGenerateBibAPI(APIView):
    """
    Triggers the release_bib() method for all users missing a BIB.
    Matches the logic in generate_bibs_view from views.py.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        # We filter exactly like your working web view:
        # Find registrations where bib_id is null OR an empty string
        target_regs = Registration.objects.filter(
            Q(bib_id__isnull=True) | Q(bib_id__exact='')
        )
        
        count = 0
        errors = []
        
        for reg in target_regs:
            try:
                # Calling the method defined in your Registration model
                new_bib = reg.release_bib() 
                if new_bib:
                    count += 1
            except Exception as e:
                errors.append(f"Error for {reg.name}: {str(e)}")
                continue 
                
        return Response({
            "message": f"Successfully generated {count} BIBs.",
            "errors": errors if errors else None
        }, status=status.HTTP_200_OK)

class TimeEntryAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        entries = TimeEntry.objects.all()[:50]
        serializer = TimeEntrySerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TimeEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)