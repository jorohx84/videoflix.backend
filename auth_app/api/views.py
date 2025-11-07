from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from django_rq import enqueue
from .utils import send_activation_email
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # JWT erstellen
        refresh = RefreshToken.for_user(user)

        # Asynchron E-Mail versenden
        enqueue(send_activation_email, user.email, str(refresh.access_token))

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
