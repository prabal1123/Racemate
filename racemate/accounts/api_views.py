from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import LoginSerializer, UserSerializer
from rest_framework import generics, permissions
import random
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import EmailOTP
from .utils import send_azure_otp 
from .serializers import ProfileSerializer
from .models import Profile
from django.contrib.auth import login as django_login

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            
            # Prepare JSON response (Access token only)
            response_data = {
                'user': UserSerializer(user).data,
                'access': tokens['access'],
                'message': 'Login successful.'
            }
            response = Response(response_data, status=status.HTTP_200_OK)

            # Set the secure Refresh Token cookie
            response.set_cookie(
                key='refresh_token',
                value=tokens['refresh'],
                httponly=True,
                secure=True, # Set to False if testing on local HTTP
                samesite='Lax',
                max_age=24 * 60 * 60 * 7
            )
            return response
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Prepare success response
            response = Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)
            
            # Shred the passport / Delete the cookie
            response.delete_cookie('refresh_token')
            
            return response
        except Exception:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
    


# class SendEmailOTPAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         email = request.data.get('email')

#         if not email:
#             return Response({'error': 'Email required'}, status=400)

#         otp = str(random.randint(100000, 999999))

#         EmailOTP.objects.create(email=email, code=otp)

#         # For now (TESTING)
#         print(f"OTP for {email}: {otp}")

#         # Later enable email:
#         # send_mail(
#         #     subject='Your OTP Code',
#         #     message=f'Your OTP is {otp}',
#         #     from_email='noreply@example.com',
#         #     recipient_list=[email],
#         # )

#         return Response({'message': 'OTP sent'})

class SendEmailOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email required'}, status=400)

        otp = str(random.randint(100000, 999999))

        # Save to DB
        EmailOTP.objects.create(email=email, code=otp)

        # Trigger Azure Email
        email_sent = send_azure_otp(email, otp)

        if email_sent:
            return Response({'message': 'OTP sent successfully to your email'})
        else:
            # Fallback to terminal so you can still log in if Azure fails
            print(f"FAILED TO SEND EMAIL. OTP for {email}: {otp}")
            return Response({'error': 'Failed to send email, please check server logs'}, status=500)


# class VerifyEmailOTPAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         email = request.data.get('email')
#         code = request.data.get('otp')

#         otp_obj = EmailOTP.objects.filter(email=email, code=code).last()

#         if not otp_obj or not otp_obj.is_valid():
#             return Response({'error': 'Invalid or expired OTP'}, status=400)

#         user, created = User.objects.get_or_create(
#             email=email,
#             defaults={'username': email}
#         )

#         tokens = get_tokens_for_user(user)

#         # 1. Prepare the JSON response (ONLY the Fast Pass / Access Token)
#         response_data = {
#             'user': UserSerializer(user).data,
#             'access': tokens['access'], 
#             'message': 'Login successful via OTP'
#         }
        
#         response = Response(response_data)

#         # 2. Put the Master ID (Refresh Token) in the secure vault (HTTP-Only Cookie)
#         response.set_cookie(
#             key='refresh_token',
#             value=tokens['refresh'],
#             httponly=True,  # JavaScript cannot read this
#             secure=True,    # Use True in production (HTTPS). Set to False if testing on localhost HTTP
#             samesite='Lax', # Protects against CSRF attacks
#             max_age=24 * 60 * 60 * 7 # Cookie lasts for 7 days
#         )

#         return response

class VerifyEmailOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('otp')

        # Fetch the most recent OTP record matching the email and code
        otp_obj = EmailOTP.objects.filter(email=email, code=code).last()

        if not otp_obj or not otp_obj.is_valid():
            return Response({'error': 'Invalid or expired OTP'}, status=400)

        # Get existing user by email, or create one if none exists
        user = User.objects.filter(email=email).order_by('date_joined').first()
        if not user:
            user = User.objects.create_user(
                username=email,
                email=email,
            )

        # Log the user into the traditional Django Session framework.
        # Passing 'backend' resolves the ValueError caused by having multiple auth backends configured.
        django_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        request.session.modified = True
        request.session.save()

        # Generate JWT tokens for API clients if needed
        tokens = get_tokens_for_user(user)

        response_data = {
            'user': UserSerializer(user).data,
            'access': tokens['access'],
            'message': 'Login successful via OTP'
        }

        response = Response(response_data)
        
        # Set the refresh token cookie
        # NOTE: secure=False is used here so the cookie works over unencrypted HTTP (like your AWS IP address).
        # Remember to switch secure=True when you point a domain with HTTPS to your AWS instance!
        response.set_cookie(
            key='refresh_token',
            value=tokens['refresh'],
            httponly=True,
            secure=False,  
            samesite='Lax',
            max_age=24 * 60 * 60 * 7
        )

        return response
    
    
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Returns the profile of the currently logged-in user
        return self.request.user.profile
    

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # Grab the token from the browser's cookies
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({"error": "Authentication credentials were not provided."}, status=401)

        # Trick SimpleJWT into thinking it was in the request body
        request.data['refresh'] = refresh_token
        
        # Let SimpleJWT do its normal validation and generate a new Access Token
        return super().post(request, *args, **kwargs)