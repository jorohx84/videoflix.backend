from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django_rq import enqueue, get_queue
from .serializers import CustomTokenObtainSerializer, PasswordResetConfirmSerializer, RegisterSerializer
from .utils import activate_user, send_activation_email, send_password_reset_email_task


class RegisterView(APIView):
    """
    API view to handle user registration.

    This view accepts user registration data via POST, validates it using
    `RegisterSerializer`, creates a new inactive user, and enqueues an 
    email task to send the account activation email.

    Methods:
        post(request):
            Handles POST requests to register a new user. Returns a success
            message if registration is successful and the activation email
            task has been enqueued.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_active = False
        user.save()

        enqueue(send_activation_email, user)

        return Response({
            "message": "Registration successful. Please check your email to activate your account."
        }, status=status.HTTP_201_CREATED)



        
class ActivateAccountView(APIView):
    """
    API view to handle user account activation via email link.

    This view accepts a GET request with a base64-encoded user ID (`uidb64`)
    and an activation token. It attempts to activate the corresponding user
    using the `activate_user` helper function. 

    Methods:
        get(request, uidb64, token):
            Handles GET requests for account activation. Redirects the user
            based on whether activation was successful.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, uidb64, token):
        user = activate_user(uidb64, token)
        if user:
            return Response({"status": "activated"}, status=200)
        else:
            return Response({"status": "invalid"}, status=400)



class LoginView(APIView):
    """
    API view to handle user login and JWT token issuance.

    This view accepts user credentials via POST, validates them using
    `CustomTokenObtainSerializer`, and returns a success response with
    the user information. Access and refresh JWT tokens are set as
    HttpOnly cookies to support secure cookie-based authentication.

    Attributes:
        permission_classes (list): Allows any user (authenticated or not)
                                   to access this view.

    Methods:
        post(request):
            Handles POST requests for user login. Validates credentials,
            generates JWT tokens, sets them as cookies, and returns a
            success response with basic user information.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        serializer = CustomTokenObtainSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({
            "detail": "Login successful",
            "user":{
                "id": user.id,
                "username": user.username,
            }
        }, status=status.HTTP_200_OK)

    
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            samesite='Lax'
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            samesite='Lax'
        )

        return response



      
class CookieTokenRefreshView(APIView):
    """
    API view to refresh JWT access tokens using a refresh token stored in cookies.

    This view reads the `refresh_token` from HttpOnly cookies, validates it,
    and issues a new access token if the refresh token is valid. The new
    access token is set as an HttpOnly cookie. Handles missing or invalid
    tokens gracefully with appropriate HTTP responses.

    Attributes:
        permission_classes (list): Allows any user (authenticated or not)
                                   to access this view.

    Methods:
        post(request):
            Handles POST requests to refresh the JWT access token. Returns
            a success response with the new access token set as a cookie,
            or an error response if the refresh token is missing or invalid.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token fehlt."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            response = Response(
                {"detail": "Token refreshed", "access": access_token},
                status=status.HTTP_200_OK,
            )
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=15 * 60, 
            )
            return response

        except TokenError:
            return Response(
                {"detail": "Ungültiger oder abgelaufener Refresh-Token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        


class PasswordResetRequestView(APIView):
    """
    API view to handle password reset requests.

    This view accepts a user's email via POST, checks if a corresponding
    user exists, and enqueues a task to send a password reset email. For
    security reasons, the response is the same whether or not the user
    exists, preventing account enumeration.

    Attributes:
        permission_classes (list): Allows any user (authenticated or not)
                                   to access this view.

    Methods:
        post(request):
            Handles POST requests to initiate a password reset. Validates
            the presence of an email, enqueues the password reset email task,
            and returns a generic success response.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "E-Mail is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
          
            return Response(
                {"detail": "An email has been sent to reset your password."},
                status=status.HTTP_200_OK
            )

        
        queue = get_queue('default')
        queue.enqueue(send_password_reset_email_task, user.id)

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK
        )
    


class LogoutView(APIView):
    """
    API view to handle user logout by blacklisting the refresh token.

    This view reads the `refresh_token` from HttpOnly cookies, blacklists it
    to prevent further use, and deletes both the access and refresh token
    cookies. If the refresh token is missing or invalid, appropriate error
    responses are returned.

    Attributes:
        permission_classes (list): Allows any user (authenticated or not)
                                   to access this view.

    Methods:
        post(request):
            Handles POST requests to log out a user. Blacklists the refresh
            token, clears authentication cookies, and returns a success
            response.
    """
    permission_classes = [AllowAny]  
    authentication_classes = []
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"detail": "Refresh-Token fehlt."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist() 
        except TokenError:
            return Response({"detail": "Ungültiger Refresh-Token."}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
                            status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
    


class PasswordResetConfirmView(APIView):
    """
    API view to confirm and complete a password reset.

    This view accepts a POST request with new password data, validates it
    using `PasswordResetConfirmSerializer`, and sets the new password for
    the user identified by `uidb64` and `token`. It ensures the token is
    valid and not expired before updating the password.

    Attributes:
        permission_classes (list): Empty list allows custom authentication
                                   handling if required.

    Methods:
        post(request, uidb64, token):
            Handles POST requests to reset a user's password. Validates the
            provided data, verifies the token, updates the password, and
            returns a success or error response.
    """
    permission_classes = [AllowAny]  
    authentication_classes = []
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK)