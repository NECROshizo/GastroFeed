from rest_framework import serializers
from djoser import serializers as djoser_serializers
# .serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from food.models import (
    Tag,
    Ingredients,
    Recipes,
    IngredientsRecipes,
)


User = get_user_model()


class UserCreateSerializer(djoser_serializers.UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserSerializer(djoser_serializers.UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')
