from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from food.models import (
    Tag,
    Ingredients,
    Recipes,
    IngredientsRecipes,

)
from .permission import RecipiesPermisionUserAutherAdmin
from .paginations import FoodgrammPagination
from .serializers import (
    UserSerializer,
    TagSerializer,
    IngredientsSerializer,
    RecipesSerializer,
    # RecipesCreateSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # pagination_class = FoodgrammPagination
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = FoodgrammPagination
    permission_classes = (permissions.IsAdminUser,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', )


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    pagination_class = FoodgrammPagination
    permission_classes = (RecipiesPermisionUserAutherAdmin,)
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('tags',)
