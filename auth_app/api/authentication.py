from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom authentication class that retrieves the JWT access token from
    an HttpOnly cookie instead of the Authorization header.

    Extends:
        JWTAuthentication: SimpleJWT's default authentication class.
    """
    def authenticate(self, request):
      
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None  

        validated_token = self.get_validated_token(access_token)

        return self.get_user(validated_token), validated_token
