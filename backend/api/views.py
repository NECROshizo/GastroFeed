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

)
from rest_framework.generics import get_object_or_404

from .permission import RecipiesPermisionUserAutherAdmin
from .paginations import FoodgrammPagination
from .serializers import (
    UserSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeBriefSerializer,
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # pagination_class = FoodgrammPagination
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


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
