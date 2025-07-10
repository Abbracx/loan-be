from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from djoser.serializers import UserCreateSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from .models import Gender

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    gender = serializers.ChoiceField(choices=Gender.choices)
    phone_number = PhoneNumberField()
    profile_photo = serializers.ImageField()
    country = CountryField()
    city = serializers.CharField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField(source="get_full_name")

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "gender",
            "phone_number",
            "profile_photo",
            "country",
            "city",
            "is_staff",
            "is_active",
            "date_joined",
        ]
    
    def get_gender(self, obj):
        return obj.gender
    
    def get_phone_number(self, obj):
        return str(obj.phone_number) if obj.phone_number else None
    
    def get_profile_photo(self, obj):
        return obj.profile_photo.url if obj.profile_photo else None

    def get_first_name(self, obj):
        return obj.first_name.title()

    def get_last_name(self, obj):
        return obj.last_name.title()

    def get_full_name(self, obj):
        return f"{obj.first_name.title()} {obj.last_name.title()}"

    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        if instance.is_superuser:
            representation["admin"] = True
        return representation


class CreateUserSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "password"]