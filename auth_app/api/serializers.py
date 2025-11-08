# from django.contrib.auth.models import AbstractUser
# from rest_framework import serializers
# from ..models import CustomUser



# class RegisterSerializer(serializers.ModelSerializer):
#     confirmed_password = serializers.CharField(write_only=True)

#     class Meta:
#         model = CustomUser  # direkt AbstractUser
#         fields = ('email', 'password', 'confirmed_password')
#         extra_kwargs = {'password': {'write_only': True}}

#     def validate(self, data):
#         if data['password'] != data['confirmed_password']:
#             raise serializers.ValidationError("Passwords do not match")
#         return data

#     def create(self, validated_data):
#         validated_data.pop('confirmed_password')
#         # username auf email setzen, da AbstractUser ein username Feld hat
#         validated_data['username'] = validated_data['email']
#         return CustomUser.objects.create_user(**validated_data)

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirmed_password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        # Passwortbestätigung prüfen
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirmed_password')

        # ⚠️ Trick: username = email, da das Standardmodell username verlangt
        user = User.objects.create_user(
            username=validated_data['email'],   # <- Hier passiert die Magie!
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Optional: direkt deaktivieren bis zur Aktivierung per E-Mail
        user.is_active = False
        user.save()

        return user









class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields.pop("username")
 

    def validate(self, attrs):
        
        email = attrs['email']
        password = attrs['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid password or email")
    
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password or email")
        
        # data = super().validate({
        #     self.username_field:getattr(user, self.username_field),
        #     "password": password
        # })
        attrs["username"]=user.username
        data = super().validate(attrs)
        return data
    

# class CustomTokenObtainSerializer(TokenObtainPairSerializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     # Überschreibe das Feld, das SimpleJWT für den Login erwartet
#     username_field = 'email'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Entferne das automatisch hinzugefügte username-Feld
#         if 'username' in self.fields:
#             self.fields.pop('username')
#         # Füge das email-Feld als username_field hinzu
#         self.fields[self.username_field] = self.fields.pop('email')

#     def validate(self, attrs):
#         email = attrs['email']
#         password = attrs['password']

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Invalid email or password")

#         if not user.check_password(password):
#             raise serializers.ValidationError("Invalid email or password")

#         # SimpleJWT erwartet hier das Klartext-Passwort
#         data = super().validate({
#             self.username_field: email,
#             'password': password
#         })

#         self.user = user
#         return data