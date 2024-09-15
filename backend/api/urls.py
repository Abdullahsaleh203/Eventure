from django.urls import path, include
from . import views
from .views import MyTokenObtainPairView
from .views import RegisterView, ProfileViewSet, ChangePasswordView, LoginView, request_password_reset, confirm_password_reset, ProfileViewSet, EventViewSet

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'event', EventViewSet, basename='event')
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('request-password-reset/', request_password_reset, name='request_password_reset'),
    path('confirm-password-reset/', confirm_password_reset, name='confirm_password_reset'),
]


