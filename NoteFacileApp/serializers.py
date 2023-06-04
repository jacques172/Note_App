from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    # Serializer for the User model

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        # Create a new User instance with the validated data
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        # Set the password using the set_password method to properly hash it
        user.set_password(validated_data['password'])
        user.save()
        return user


