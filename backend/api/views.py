from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions, status, viewsets
# from django.contrib.auth.models import User
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileSerializer,
    EventSerializer,
    ChangePasswordSerializer,
    MyTokenObtainPairSerializer,
    MyTokenObtainPairSerializerFull
    )
from .models import Profile, Event
from .authentication import CustomUserAuthentication
from rest_framework.decorators import action
from .services.weather import WeatherService
from .services.maps import MapsService


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# @api_view(['GET'])
# def getRoutes(request):
#     routes = [
#         '/api/token/',
#         '/api/token/refresh/',
#         '/api/register/',
#         '/api/profile/',
#         '/api/change-password/',
#         '/api/request-password-reset/',
#         '/api/confirm-password-reset/',
#     ]
#     return Response(routes)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializerFull
    permission_classes = [permissions.AllowAny]

# class UserProfileView(generics.RetrieveUpdateAPIView):
#     queryset = User.objects.all()
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = UserSerializer

#     def get_object(self):
#         return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def request_password_reset(request):
    email = request.data.get('email')
    if not email:
        return Response({"email": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"email": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    token = default_token_generator.make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}/"
    send_mail(
        'Password Reset Request',
        f'Click the link below to reset your password:\n{reset_url}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    return Response({"detail": "Password reset link sent."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def confirm_password_reset(request):
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    if not token or not new_password:
        return Response({"detail": "Token and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=request.data.get('email'))
    except User.DoesNotExist:
        return Response({"email": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing user profiles.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # authentication_classes = [CustomUserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # Override the get_queryset to ensure users can only manage their own profile
    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def get_object(self):
        # Always return the current user's profile without requiring the profile ID in the URL
        return get_object_or_404(Profile, user=self.request.user)

    # Override retrieve to get the user's own profile
    def retrieve(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    # Override update to ensure users can update their own profile
    def update(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=request.user)
        print(profile)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Override create to ensure users create their own profile
    def create(self, request, *args, **kwargs):
        if Profile.objects.filter(user=request.user).exists():
            return Response({"error": "Profile already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing user events.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    # authentication_classes = [CustomUserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # Override the get_queryset to filter by authenticated user
    def get_queryset(self):
        print(self.request)
        return Event.objects.filter(owner=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        event = self.get_object()  # Get the event that is being deleted
        event_title = event.title  # Store the title (or any other details) before deletion
        event_owner = event.owner  # Store owner for custom message
        response = super().destroy(request, *args, **kwargs)
        # Send a custom message or log after deletion
        if response.status_code == status.HTTP_204_NO_CONTENT:
            return Response({'message': f"Event '{event_title}' owned by {event_owner} has been successfully deleted."})

    # Custom action to get the weather for the event
    @action(detail=True, methods=['get'], url_path='weather')
    def get_weather(self, request, pk=None):
        event = self.get_object()
        if event.status.name == "Offline":
            weather_info = WeatherService.get_weather(event.location)
            return Response(weather_info)
        return Response({"error": "Weather forecast only available for offline events."})

    # Custom action to get the route to the event
    @action(detail=True, methods=['get'], url_path='route')
    def get_route(self, request, pk=None):
        event = self.get_object()
        print(event.status)
        if event.status == "OF":
            profile = event.owner.profile
            directions = MapsService.get_directions(profile.location, event.location)
            return Response(directions)
        return Response({"error": "Directions only available for offline events."})