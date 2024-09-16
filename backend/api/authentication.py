from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
# from django.contrib.auth.models import User


class CustomUserAuthentication(BaseAuthentication):
    def authenticate(self, request):
        try:
            print(request.header)
            user = request.user
            if not user.is_authenticated:
                raise AuthenticationFailed('User is not authenticated')
        except e:
            raise AuthenticationFailed('User is not authenticated')
        return (user, None)
