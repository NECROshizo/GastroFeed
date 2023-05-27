from django.contrib.auth import get_user_model
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .utils import add_ingredients_in_recipe, check_object
from food.models import (
    Ingredient,
    IngredientsRecipes,
    Recipe,
    Tag,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели CookUser для полного представления объекта
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True, )

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj: User):
        """Проверить на вхождение в подписки"""
        return check_object(self, obj.subscriber)

    def create(self, validated_data):
        """Создать пользователя"""
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient"""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Recipe для полного представления объекта
    """
    tags = TagSerializer(many=True, read_only=True, )
    author = UserSerializer(read_only=True, )
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True, )
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True, )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj: Recipe):
        """Получить ингредиенты рецепта с количеством"""
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_in_recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj: Recipe):
        """Проверить на вхождение в избранное"""
        return check_object(self, obj.favorit_recipe)

    def get_is_in_shopping_cart(self, obj: Recipe):
        """Проверить на вхождение в корзину покупок"""
        return check_object(self, obj.shoping_card_recipe)

    def validate(self, data):
        """Валидмровать и нормализовать данные для создания рецепта"""
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        user = self.context.get('request').user

        if not tags:
            raise serializers.ValidationError('Теги необходиый атрибут')
        # tags_exists = Tag.objects.filter(id__in=tags).values('id')
        # tags_missing = [tag for tag in tags if tag not in tags_exists]
        # if tags_missing: # TODO str != int
        #     raise serializers.ValidationError(
        #         # f'Теги {", ".join(tags_missing)} не существуют')
        #         'Тег не существуют')

        if not ingredients:
            raise serializers.ValidationError(
                'Ингредиенти необходиый атрибут')
        ingredient_amount = list()
        ingredient_missing, amount_incorrect = list(), list()
        for ingredient in ingredients:
            id, amount = ingredient.values()
            ingredient_obj = Ingredient.objects.get(id=id)
            if not ingredient_obj:
                ingredient.append(id)
            elif int(amount) < 1:
                amount_incorrect.append(id)
            ingredient_amount.append((ingredient_obj, amount,))

        if ingredient_missing:
            raise serializers.ValidationError(
                f'Ингредиентs {", ".join(ingredient_missing)} не существуют')
        if amount_incorrect:
            raise serializers.ValidationError(
                f'У ингредиентов {", ".join(amount_incorrect)}'
                f'некоректныое количество'
            )
        data.update({
            'tags': tags,
            'ingredients': ingredient_amount,
            'author': user
        })
        return data

    def create(self, validated_data):
        """Создать рецепт"""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        add_ingredients_in_recipe(IngredientsRecipes, recipe, ingredients)
        recipe.tags.set(tags)
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        """Обновить рецепт"""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        serializers.ValidationError(validated_data)
        if tags:
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            add_ingredients_in_recipe(
                IngredientsRecipes, instance, ingredients)
        return super().update(instance, validated_data)


class RecipeBriefSerializer(serializers.ModelSerializer):
    """Сериализатор Recipe для емкого отображения  """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserSubscriptionsSerializer(UserSerializer):
    """Сериализатор UserCook для отображения модели в качестве подписаного """
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes(self, obj: User):
        """Получить рецепты подписаного пользователя"""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        serializer = RecipeBriefSerializer(recipes, many=True,)
        return serializer.data

    def get_recipes_count(self, obj: User):
        """Получить количество рецептов подписаного пользователя"""
        return obj.recipes.count()

    def get_is_subscribed(self, obj: User):
        """Проверить подписан ли пользователь, хоть и всегда да"""
        return True
