from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from food.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientsRecipes,
    Favorit,
    ShoppingCart,
)
from user.models import Subscriptions
from rest_framework.generics import get_object_or_404

from .permission import RecipiesPermisionUserAutherAdmin
from .paginations import FoodgrammPagination
from .serializers import (
    UserSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeBriefSerializer,
    UserSubscriptionsSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = FoodgrammPagination
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=UserSubscriptionsSerializer,
    )
    def subscriptions(self, request: WSGIRequest):
        pages = self.paginate_queryset(
            User.objects.filter(subscriber__user=request.user)
        )
        serializer = self.get_serializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        serializer_class=UserSubscriptionsSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request: WSGIRequest, pk):
        user = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            if user.subscriber.filter(user=request.user).exists():
                return Response(
                    {'errors': 'Уже в потписан'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscriptions.objects.create(user=request.user, subscriber=user)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscriptions = get_object_or_404(
                Subscriptions, user=request.user, subscriber=user)
            subscriptions.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = FoodgrammPagination
    permission_classes = (permissions.IsAdminUser,)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', )


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = FoodgrammPagination
    permission_classes = (RecipiesPermisionUserAutherAdmin,)
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('tags',)

    @action(
        detail=True,
        methods=['post', 'delete'],
        serializer_class=RecipeBriefSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request: WSGIRequest, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if recipe.favorit_recipe.filter(user=request.user).exists():
                return Response(
                    {'errors': 'Уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorit.objects.create(user=request.user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorit = get_object_or_404(
                Favorit, user=request.user, recipe=recipe)
            favorit.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['get', 'post', 'delete'],
        serializer_class=RecipeBriefSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request: WSGIRequest, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if recipe.shoping_card_recipe.filter(user=request.user).exists():
                return Response(
                    {'errors': 'Уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            favorit = get_object_or_404(
                ShoppingCart, user=request.user, recipe=recipe)
            favorit.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
