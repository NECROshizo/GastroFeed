from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .filters import RecipeFilter
from .paginations import FoodgrammPagination
from .permission import RecipiesPermisionUserAutherAdmin
from .serializers import (IngredientSerializer, RecipeBriefSerializer,
                          RecipeSerializer, TagSerializer, UserSerializer,
                          UserSubscriptionsSerializer)
from .utils import (
    add_obj_in_table, delete_obj_in_table, make_content_file, sent_file)
from food.models import Ingredient, IngredientsRecipes, Recipe, Tag

User = get_user_model()


class UserViewSet(DjoserViewSet, viewsets.ModelViewSet):
    """Представление работы с User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = FoodgrammPagination

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=UserSubscriptionsSerializer,
    )
    def subscriptions(self, request: WSGIRequest) -> Response:
        pages = self.paginate_queryset(
            User.objects.filter(subscriber__user=request.user)
        )
        serializer = self.get_serializer(pages, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=UserSubscriptionsSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request: WSGIRequest, id: str) -> Response:
        user = get_object_or_404(User, id=id)
        return add_obj_in_table(
            self.get_serializer, request.user, user, user.subscriber)

    @subscribe.mapping.delete
    def subscriber_delete(self, request: WSGIRequest, id: str) -> Response:
        user = get_object_or_404(User, id=id)
        return delete_obj_in_table(
            request.user, user.subscriber)


class TagsViewSet(viewsets.ModelViewSet):
    """Представление работы с Tag"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientsViewSet(viewsets.ModelViewSet):
    """Представление работы с Ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    pagination_class = None
    search_fields = ('^name', )


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = FoodgrammPagination
    permission_classes = (RecipiesPermisionUserAutherAdmin,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self) -> QuerySet[Recipe]:
        """Получить queryset в зависимости от переданных параметров"""
        user = self.request.user
        if user.is_anonymous:
            return super().get_queryset()
        if self.request.query_params.get('is_favorited'):
            return Recipe.objects.filter(favorit_recipe__user=user)
        if self.request.query_params.get('is_in_shopping_cart'):
            return Recipe.objects.filter(shoping_card_recipe__user=user)
        return super().get_queryset()

    @action(
        detail=True,
        methods=['post'],
        serializer_class=RecipeBriefSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request: WSGIRequest, pk: str) -> Response:
        """Добавить рецепт в избранное"""
        recipe = get_object_or_404(Recipe, id=pk)
        return add_obj_in_table(
            self.get_serializer, request.user, recipe,
            recipe.favorit_recipe)

    @favorite.mapping.delete
    def favotite_delete(self, request: WSGIRequest, pk: str) -> Response:
        """Удалить рецепт из избранного"""
        recipe = get_object_or_404(Recipe, id=pk)
        return delete_obj_in_table(
            request.user, recipe.favorit_recipe)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=RecipeBriefSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request: WSGIRequest, pk: str) -> Response:
        """Добавить рецепт в корзину"""
        recipe = get_object_or_404(Recipe, id=pk)
        return add_obj_in_table(
            self.get_serializer, request.user, recipe,
            recipe.shoping_card_recipe)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request: WSGIRequest, pk: str) -> Response:
        """Удалить рецепт из корзины"""
        recipe = get_object_or_404(Recipe, id=pk)
        return delete_obj_in_table(
            request.user, recipe.shoping_card_recipe)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request: WSGIRequest) -> HttpResponse:
        """Отправить сформированный список ингредиентов из рецептов"""
        user = request.user
        file_name = f'{user.username}-byu-list.txt'
        all_ingredient = IngredientsRecipes.objects.filter(
            recipe__shoping_card_recipe__user=user
        ).order_by(
            'ingredient__name'
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        )
        content_file = make_content_file(all_ingredient)
        return sent_file(content_file, file_name)
