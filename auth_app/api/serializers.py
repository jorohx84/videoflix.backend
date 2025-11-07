from django.contrib.auth.models import AbstractUser
from rest_framework import serializers
from ..models import CustomUser
class RegisterSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser  # direkt AbstractUser
        fields = ('email', 'password', 'confirmed_password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirmed_password')
        # username auf email setzen, da AbstractUser ein username Feld hat
        validated_data['username'] = validated_data['email']
        return CustomUser.objects.create_user(**validated_data)

