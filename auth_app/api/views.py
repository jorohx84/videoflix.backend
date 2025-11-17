from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, CustomTokenObtainSerializer, PasswordResetConfirmSerializer
from django_rq import enqueue
from .utils import send_activation_email, activate_user
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from .utils import send_password_reset_email_task
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django_rq import get_queue
from django.utils.http import urlsafe_base64_decode

class RegisterView(APIView):
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


from django.shortcuts import redirect
from rest_framework.views import APIView

class ActivateAccountView(APIView):
    """
    Aktiviert den Benutzer über den Token-Link
    und leitet ihn anschließend auf die Login-Seite weiter.
    """
    def get(self, request, uidb64, token):
        user = activate_user(uidb64, token)
        if user:
            # Erfolgreich aktiviert → auf Login-Seite weiterleiten
            return redirect("http://127.0.0.1:5500/pages/auth/login.html?activated=true")
        else:
            # Aktivierung fehlgeschlagen → Fehlermeldungsseite
            return redirect("http://127.0.0.1:5500/pages/auth/activation-failed.html")
        



class LoginView(APIView):
    permission_classes = [AllowAny]
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
                "user": user.username,
            }
        }, status=status.HTTP_200_OK)

    
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            samesite='Strict'
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            samesite='Strict'
        )

        return response



      
class CookieTokenRefreshView(APIView):
    """
    POST /api/token/refresh/
    Description:
        Gibt ein neues Zugangstoken aus, wenn der alte Access-Token abgelaufen ist.
        Der Token im Response hat keine Verwendung für das FrontEnd,
        da HTTP-Only Cookies verwendet werden.
    """

    permission_classes = [AllowAny]

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
    Request a password reset email.
    """
    permission_classes = [AllowAny]

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
            # Sicherheitsmaßnahme: wir geben keinen Hinweis, dass der User nicht existiert
            return Response(
                {"detail": "An email has been sent to reset your password."},
                status=status.HTTP_200_OK
            )

        # Optional: Queue mit django-rq für asynchrone Mail
        queue = get_queue('default')
        queue.enqueue(send_password_reset_email_task, user.id)

        # Wenn du es synchron machen willst:
        # send_password_reset_email(user)

        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK
        )
    


class LogoutView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({"detail": "Refresh-Token fehlt."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist() 
        except TokenError:
            return Response({"detail": "Ungültiger Refresh-Token."}, status=status.HTTP_401_UNAUTHORIZED)

        # Cookies löschen
        response = Response({"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
                            status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response
    


class PasswordResetConfirmView(APIView):
    permission_classes = []  

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