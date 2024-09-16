#!/usr/bin/env python3
"""
The leader who manages URL's and Models
"""
from django.http import JsonResponse
from .services.maps import MapsService  # Assuming MapsService handles Google Maps API requests
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, permissions, status, viewsets
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    EventSerializer,
    ChangePasswordSerializer,
    MyTokenObtainPairSerializer,
    MyTokenObtainPairSerializerFull
    )
from .models import Profile, Event
from .authentication import CustomUserAuthentication
from .services.weather import WeatherService
from .services.maps import MapsService


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view.
    """
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class LoginView(TokenObtainPairView):
    """
    API view for user login with JWT token.
    """
    serializer_class = MyTokenObtainPairSerializerFull
    permission_classes = [permissions.AllowAny]


class ChangePasswordView(generics.UpdateAPIView):
    """
    API view for allowing users to change their password.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        """
        Retrieve the current authenticated user object.
        """
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Handle password change logic.
        Checks old password, validates, and updates to new password.
        """
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check if the old password is correct
            if not self.object.check_password(
                serializer.data.get("old_password")
                    ):
                return Response(
                    {
                        "old_password": ["Wrong password."]
                    },
                    status=status.HTTP_400_BAD_REQUEST)
            # Set new password
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"detail": "Password updated successfully."},
                status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing user profiles.
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # authentication_classes = [CustomUserAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # Override the get_queryset to
    # ensure users can only manage their own profile
    def get_queryset(self):
        """
        Override to ensure users can only manage their own profile.
        """
        return Profile.objects.filter(user=self.request.user)

    def get_object(self):
        """
        Always return the current user's profile without
        requiring the profile ID in the URL.
        """
        return get_object_or_404(Profile, user=self.request.user)

    # Override retrieve to get the user's own profile
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the authenticated user's profile.
        """
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    # Override update to ensure users can update their own profile
    def update(self, request, *args, **kwargs):
        """
        Update the authenticated user's profile.
        """
        profile = get_object_or_404(Profile, user=request.user)
        print(profile)
        serializer = self.get_serializer(
            profile,
            data=request.data,
            partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Override create to ensure users create their own profile
    def create(self, request, *args, **kwargs):
        """
        Create a profile for the authenticated user.
        """
        if Profile.objects.filter(user=request.user).exists():
            return Response(
                {"error": "Profile already exists."},
                status=status.HTTP_400_BAD_REQUEST)

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
        """
        Override to filter events by the authenticated user.
        """
        print(self.request)
        return Event.objects.filter(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """
        Handle deletion of an event with a custom response message.
        """
        event = self.get_object()
        event_title = event.title
        event_owner = event.owner
        response = super().destroy(request, *args, **kwargs)
        # Send a custom message or log after deletion
        if response.status_code == status.HTTP_204_NO_CONTENT:
            message = f"""Event '{event_title}' owned by {event_owner}
            has been successfully deleted."""
            return Response(
                {'message': message})

    # Custom action to get the weather for the event
    @action(detail=True, methods=['get'], url_path='weather')
    def get_weather(self, request, pk=None):
        """
        Custom action to get the weather for the event.
        Only available for offline events.
        """
        event = self.get_object()
        if event.status.name == "Offline":
            weather_info = WeatherService.get_weather(event.location)
            return Response(weather_info)
        message = "Weather forecast only available for offline events."
        return Response({"error": message})

    # Custom action to get the route to the event
    @action(detail=True, methods=['get'], url_path='route')
    def get_route(self, request, pk=None):
        """
        Custom action to get directions to the event.
        Only available for offline events.
        """
        event = self.get_object()
        print(event.status)
        if event.status == "OF":
            profile = event.owner.profile
            directions = MapsService.get_directions(
                profile.location,
                event.location)
            return Response(directions)
        message = "Directions only available for offline events."
        return Response({"error": message})


@api_view(['POST'])
def request_password_reset(request):
    """
    API view for requesting password reset link via email.
    """
    email = request.data.get('email')
    if not email:
        return Response(
            {"email": "This field is required."},
            status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"email": "User with this email does not exist."},
            status=status.HTTP_400_BAD_REQUEST)

    # Generate token and send password reset email
    token = default_token_generator.make_token(user)
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}/"
    send_mail(
        'Password Reset Request',
        f'Click the link below to reset your password:\n{reset_url}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
    return Response(
        {"detail": "Password reset link sent."},
        status=status.HTTP_200_OK)


@api_view(['POST'])
def confirm_password_reset(request):
    """
    API view for confirming and completing password reset.
    """
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    if not token or not new_password:
        return Response(
            {"detail": "Token and new password are required."},
            status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=request.data.get('email'))
    except User.DoesNotExist:
        return Response(
            {"email": "User with this email does not exist."},
            status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Password reset successfully."},
            status=status.HTTP_200_OK)
    else:
        return Response(
            {"detail": "Invalid token."},
            status=status.HTTP_400_BAD_REQUEST)

# Get geolocation for an address
@api_view(['GET'])
def get_location(request):
    address = request.GET.get('address')
    if not address:
        return JsonResponse({'error': 'Address not provided'}, status=400)
    
    location_data = MapsService.get_location(address)
    return JsonResponse(location_data)

# Get directions between origin and destination
@api_view(['GET'])
def get_directions(request):
    origin = request.GET.get('origin')
    destination = request.GET.get('destination')
    
    if not origin or not destination:
        return JsonResponse({'error': 'Origin or destination not provided'}, status=400)
    
    directions_data = MapsService.get_directions(origin, destination)
    return JsonResponse(directions_data)