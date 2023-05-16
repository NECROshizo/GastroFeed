from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins
from djoser.views import UserViewSet
from food.models import (
    Tag,
    Ingredients,
    Recipes,
    IngredientsRecipes,
)
from .serializers import (
    UserSerializer,
)

User = get_user_model()


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
