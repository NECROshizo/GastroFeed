from rest_framework import serializers
from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from food.models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientsRecipes,
)
import json

User = get_user_model()


from django.db.models.fields.related_descriptors import create_reverse_many_to_one_manager
from rest_framework import serializers
def _check_object(
    instans_class: serializers,
    obj: create_reverse_many_to_one_manager
) -> bool:
    user = instans_class.context.get('request').user
    if user.is_anonymous:
        return False
    return obj.filter(user=user).exists()


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
        return _check_object(self, obj.subscriber)

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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializer(serializers.ModelSerializer):
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
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_in_recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj: Recipe):
        return _check_object(self, obj.favorit_recipe)

    def get_is_in_shopping_cart(self, obj: Recipe):
        return _check_object(self, obj.shoping_card_recipe)

    def validate(self, data):
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
        recipe = Recipe.objects.create(**validated_data)

        IngredientsRecipes.objects.bulk_create(
            [
                IngredientsRecipes(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=amount,
                )
                for ingredient, amount in ingredients_amount
            ]
        )
        recipe.tags.set(tags)
        recipe.save()
        return recipe

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
                        recipe=instance,
                        ingredient=ingredient,
                        amount=amount,
                    )
                    for ingredient, amount in ingredients_amount
                ]
            )
        return super().update(instance, validated_data)


class RecipeBriefSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    recipes = RecipeBriefSerializer(many=True,)
    is_subscription = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscription',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscription', 'recipes', 'recipes_count',
        )

    def get_recipes_count(self, obj: User):
        return obj.recipes.count()

    def get_is_subscription(self, obj: User):
        return True  # TODO ??????
