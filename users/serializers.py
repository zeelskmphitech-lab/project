from rest_framework import serializers
from .models import Users

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Users
        fields = ['email', 'username', 'first_name', 'last_name', 'password','is_seller']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Users(**validated_data)
        user.set_password(password) 
        user.save()
        return user