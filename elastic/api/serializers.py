from rest_framework import serializers

from elastic.api.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'address', 'phone', 'date_of_birth', 'image',
            'password', 'confirm_password', 'is_superuser', 'is_staff', 'is_active', 'user_permissions')
