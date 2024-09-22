from rest_framework import serializers

from users.models import CustomUser

from .models import Order


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "username", "email"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "order_number", "total_amount", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
