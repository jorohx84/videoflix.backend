from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, CustomTokenObtainSerializer
from django_rq import enqueue
from .utils import send_activation_email, activate_user
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # JWT erstellen
        refresh = RefreshToken.for_user(user)

        # Asynchron E-Mail versenden
        enqueue(send_activation_email, user.email, str(refresh.access_token))
        # send_activation_email(user.email, "TEST-TOKEN")
        response = Response({
            "user": {
                "id": user.id,
                "email": user.email
            },
            "token": str(refresh.access_token)  # nur Info
        }, status=status.HTTP_201_CREATED)

        # Token als HttpOnly Cookie setzen
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
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




class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        user = activate_user(uidb64, token)
        if user:
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK
            )
        return Response(
            {"message": "Activation failed."},
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginView(APIView):
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

      
