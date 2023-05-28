from django.urls import include, path, re_path
from rest_framework import routers

from .views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
    UserViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
