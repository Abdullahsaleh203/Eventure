from django.urls import path
from . import views
from .views import MyTokenObtainPairView
from django.urls import path
from .views import RegisterView, UserProfileView, ChangePasswordView, request_password_reset, confirm_password_reset

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


urlpatterns = [
    path('', views.getRoutes),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('request-password-reset/', request_password_reset, name='request_password_reset'),
    path('confirm-password-reset/', confirm_password_reset, name='confirm_password_reset'),
]


