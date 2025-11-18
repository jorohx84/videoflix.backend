from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer used for user registration.

    This serializer handles collecting user credentials, validating that
    the password fields match, and creating a new inactive user account.
    It accepts `email`, `password`, and `confirmed_password`, where
    `confirmed_password` is used only for validation and not stored.

    Methods:
        validate(data):
            Ensures that `password` and `confirmed_password` are identical.
        
        create(validated_data):
            Removes the temporary `confirmed_password` field and creates a
            new inactive user account using the provided email and password.
    """
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirmed_password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
 
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirmed_password')

        user = User.objects.create_user(
            username=validated_data['email'],  
            email=validated_data['email'],
            password=validated_data['password']
        )

     
        user.is_active = False
        user.save()

        return user


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    """
    Custom serializer used for email-based authentication with JWT.

    This serializer replaces the default username authentication by validating
    users through their email address and password. It removes the default
    `username` field, verifies the provided credentials manually, and then
    delegates token generation to SimpleJWT once the user is confirmed.

    Methods:
        __init__(*args, **kwargs):
            Removes the default `username` field inherited from the base
            serializer to allow email-only authentication.

        validate(attrs):
            Authenticates a user by email and password, attaches the
            username required by SimpleJWT, and returns the generated
            token pair.
    """
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
        
        attrs["username"]=user.username
        data = super().validate(attrs)
        return data
    



class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer used for confirming a password reset by validating new
    password inputs.

    This serializer accepts `new_password` and `confirm_password`, ensures
    that both fields match, and enforces a minimum password length. It does
    not perform the actual password change, only the validation step.

    Methods:
        validate(attrs):
            Verifies that both password fields are identical and returns
            the validated attributes.
    """
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs