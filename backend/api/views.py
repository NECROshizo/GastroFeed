from datetime import date

from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .filters import RecipeFilter
from .paginations import FoodgrammPagination
from .permission import RecipiesPermisionUserAutherAdmin
from .serializers import (IngredientSerializer, RecipeBriefSerializer,
                          RecipeSerializer, TagSerializer, UserSerializer,
                          UserSubscriptionsSerializer)
from food.models import (Favorit, Ingredient, IngredientsRecipes, Recipe,
                         ShoppingCart, Tag)
from user.models import Subscriptions

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
    def subscriptions(self, request: WSGIRequest):
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
    def subscribe(self, request: WSGIRequest, id):
        user = get_object_or_404(User, id=id)
        if user.subscriber.filter(user=request.user).exists():
            return Response(
                {'errors': 'Уже потписан'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscriptions.objects.create(user=request.user, subscriber=user)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscriber_delete(self, request: WSGIRequest, id):
        user = get_object_or_404(User, id=id)
        subscriptions = get_object_or_404(
            Subscriptions, user=request.user, subscriber=user)
        subscriptions.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    def get_queryset(self):
        """Получить queryset в зависимости от переданных параметров"""
        user = self.request.user
        if user.is_anonymous:
            return super().get_queryset()
        if self.request.query_params.get('is_favorited'):
            return Recipe.objects.filter(favorit_recipe__user=user)
        if self.request.query_params.get('is_in_shopping_cart'):
            return Recipe.objects.filter(shoping_card_recipe__user=user)
        return super().get_queryset()

    #=====================================================================
    from rest_framework import serializers
    from django.db import models
    @staticmethod
    def add_recipe_in_model(
            serialize: serializers.ModelSerializer,
            pk: int,
            user: models.Model,
            model: models.Model,
            recipe_model: models.Model,
            error_message: str = 'Уже сделано',
    ):
        recipe = get_object_or_404(recipe_model, id=pk)
        if recipe.shoping_card_recipe.filter(user=user).exists():
            return Response(
                {'errors': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        return Response(serialize(recipe).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_recipe_in_model(
            pk: int,
            user: models.Model,
            model: models.Model,
            recipe_model: models.Model,
    ):
        recipe = get_object_or_404(recipe_model, id=pk)
        model_for_recipie = get_object_or_404(
            model, user=user, recipe=recipe)
        model_for_recipie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



    @action(
        detail=True,
        methods=['post'],
        serializer_class=RecipeBriefSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request: WSGIRequest, pk):
        return self.add_recipe_in_model(
            self.get_serializer, pk, request.user, Favorit, Recipe,)
        # recipe = get_object_or_404(Recipe, id=pk)
        # if recipe.favorit_recipe.filter(user=request.user).exists():
        #     return Response(
        #         {'errors': 'Уже в избранном'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        # Favorit.objects.create(user=request.user, recipe=recipe)
        # serializer = self.get_serializer(recipe)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def favotite_delete(self, request: WSGIRequest, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorit = get_object_or_404(
            Favorit, user=request.user, recipe=recipe)
        favorit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=RecipeBriefSerializer,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request: WSGIRequest, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if recipe.shoping_card_recipe.filter(user=request.user).exists():
            return Response(
                {'errors': 'Уже в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request: WSGIRequest, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorit = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe)
        favorit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request: WSGIRequest):
        user = request.user
        all_ingredient = IngredientsRecipes.objects.filter(
            recipe__shoping_card_recipe__user=user
        ).order_by(
            'ingredient__name'
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        )

        file_name = f'{user.username}-byu-list.txt'
        content_file = [f'Список покупок от {date.today()}:\n']
        for num, ingredient in enumerate(all_ingredient, start=1):
            name, m_unit, amount = ingredient.values()
            content_file.append(f'{num}. {name} - {amount} {m_unit}\n')
        response = HttpResponse(
            content_file, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response
