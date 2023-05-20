
from rest_framework import serializers
from djoser import serializers as djoser_serializers
# .serializers import UserCreateSerializer, UserSerializer
from django.db.models import F
from django.contrib.auth import get_user_model
from food.models import (
    Tag,
    Ingredients,
    Recipes,
    IngredientsRecipes,
)


User = get_user_model()


class UserCreateSerializer(djoser_serializers.UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserSerializer(serializers.ModelSerializer):
    is_subscription = serializers.SerializerMethodField()

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
        read_only_fields = ('id', 'is_subscription',)
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscription(self, obj: User):
        request = self.context.get('request')
        return obj.user.filter(user=request.user).exists()

    # def create(self, validated_data):
    #     password = validated_data.pop('password')
    #     # validated_data.pop('id')
    #     user = User.objects.create_user(**validated_data)
    #     # user = User(
    #     #     # id=self.context.get('request').user.id,
    #     #     email=validated_data['email'],
    #     #     username=validated_data['username'],
    #     #     first_name=validated_data['first_name'],
    #     #     last_name=validated_data['last_name'],
    #     # )
    #     user.set_password(password)
    #     user.save()
    #     return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit', )


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True,)
    author = UserSerializer(read_only=True,)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            # 'is_in_shopping_cart',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj: Recipes):
        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('ingredient_in_recipe__amount')
        )
        return ingredients
