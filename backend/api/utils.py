from django.db.models.fields import related_descriptors
from rest_framework import serializers
from django.db.models import Model


def check_object(
    instans_class: serializers,
    obj: related_descriptors.ReverseManyToOneDescriptor
) -> bool:
    """
    Проверить вхождения объектов по сязи м2м по совпадению пользователя
    """
    user = instans_class.context.get('request').user
    if user.is_anonymous:
        return False
    return obj.filter(user=user).exists()


def add_ingredients_in_recipe(
    model: Model, recipe: Model, ingredients: list[tuple]
) -> None:
    """Наполнить связующию м2м таблицу"""
    model.objects.bulk_create(
        [
            model(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount,
            )
            for ingredient, amount in ingredients
        ]
    )
