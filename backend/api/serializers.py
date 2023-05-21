from rest_framework import serializers
from djoser import serializers as djoser_serializers
# .serializers import UserCreateSerializer, UserSerializer
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from food.models import (
    Tag,
    Ingredients,
    Recipes,
    IngredientsRecipes,
)
import json
from django.db import transaction

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscription = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscription',
            'password',
        )
        read_only_fields = ('is_subscription',)
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscription(self, obj: User):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return obj.subscription.filter(subscriber=request.user).exists()

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit',)


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True,)
    author = UserSerializer(read_only=True, )
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True, )
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True, )
    image = Base64ImageField()

    class Meta:
        model = Recipes
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
        # read_only_fields = ('id',)

    def get_ingredients(self, obj: Recipes):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_in_recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj: Recipes):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorit_recipe.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj: Recipes):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.shoping_card_recipe.filter(user=user).exists()

    # def validate_tags(self, value):
    #     # if not value:
    #     #     raise serializers.ValidationError('Теги необходиый атрибут')
    #     tags_exists = Tag.objects.filter(id__in=value).values('id')
    #     tags_missing = [tag for tag in value if tag not in tags_exists]
    #     if tags_missing:
    #         raise serializers.ValidationError(
    #             f'Теги {", ".join(tags_missing)} не существуют')
    #     return value

    # def validate_ingredients(self, value: list[dict]):
    #     # if not value:
    #     #     raise serializers.ValidationError(
    #     #         'Ингредиенти необходиый атрибут')
    #     ingredient_missing, amount_incorrect = list(), list()
    #     for ingredient in value:
    #         id, amount = ingredient.values()
    #         if not Ingredients.objects.filter(id=id).exists():
    #             ingredient.append(id)
    #         elif amount < 1:
    #             amount_incorrect.append(id)
    #     if ingredient_missing:
    #         raise serializers.ValidationError(
    #             f'Ингредиентs {", ".join(ingredient_missing)} не существуют')
    #     if amount_incorrect:
    #         raise serializers.ValidationError(
    #             f'У ингредиентов {", ".join(amount_incorrect)}'
    #             f'некоректныое количество'
    #         )
    #     return value

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        user = self.context.get('request').user

        if not tags:
            raise serializers.ValidationError('Теги необходиый атрибут')
        # tags_exists = Tag.objects.filter(id__in=tags).values('id')
        # tags_missing = [tag for tag in tags if tag not in tags_exists]
        # if tags_missing:
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
            ingredient_obj = Ingredients.objects.get(id=id)
            if not ingredient_obj:
                ingredient.append(id)
            elif amount < 1:
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
        ingredients_amount = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipes = Recipes.objects.create(**validated_data)

        IngredientsRecipes.objects.bulk_create(
            [
                IngredientsRecipes(
                    recipes=recipes,
                    ingredient=ingredient,
                    amount=amount,
                )
                for ingredient, amount in ingredients_amount
            ]
        )
        recipes.tags.set(tags)
        recipes.save()
        return recipes

    def update(self, instance, validated_data):
        ingredients_amount = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        serializers.ValidationError(validated_data)
        if tags:
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients_amount:
            instance.ingredients.clear()

            IngredientsRecipes.objects.bulk_create(
                [
                    IngredientsRecipes(
                        recipes=instance,
                        ingredient=ingredient,
                        amount=amount,
                    )
                    for ingredient, amount in ingredients_amount
                ]
            )
        return super().update(instance, validated_data)
