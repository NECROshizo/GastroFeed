from datetime import date

from django.conf import settings
from django.db.models import Model
from django.db.models.fields import related_descriptors
from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.response import Response


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


def get_messege_incorect_obj(
    name: tuple[str],
    missing: list[str],
    error: tuple[str] = settings.DEFOLT_MESSAGE_INCORECT_OBJ
) -> str:
    """Получение формотируемой строки ошибки"""
    return (f'{name[(f := (len(missing) == 1))]} '
            f'{", ".join(missing)} '
            f'{error[f]}.')


def check_tags(tags: list[str], model: Model) -> list[str]:
    """Проверить теги на соответствие"""
    if not tags:
        raise serializers.ValidationError('Теги необходиый атрибут')
    tags_exists = model.objects.filter(id__in=tags).values('id')
    tags_equivalent = map(lambda x: x.get('id'), tags_exists)
    tags_missing = [
        str(tag)
        for tag in tags
        if tag not in tags_equivalent
    ]
    if tags_missing:
        raise serializers.ValidationError(
            get_messege_incorect_obj(("Теги:", "Tег"), tags_missing))
    return tags


def check_ingredients(ingredients: list[dict], model: Model) -> list[tuple]:
    """Проверять ингредиенты на соответствие"""
    if not ingredients:
        raise serializers.ValidationError(
            'Ингредиент необходиый атрибут')
    ingredient_amount = list()
    ingredient_missing, amount_incorrect = list(), list()
    for ingredient in ingredients:
        id, amount = ingredient.values()
        ingredient_obj = model.objects.get(id=id)
        if not ingredient_obj:
            ingredient.append(str(id))
        elif int(amount) < 1:
            amount_incorrect.append(str(id))
        ingredient_amount.append((ingredient_obj, amount,))

    if ingredient_missing:
        raise serializers.ValidationError(
            get_messege_incorect_obj(
                ("Ингредиенты:", "Ингредиент"), ingredient_missing)
        )
    if amount_incorrect:
        raise serializers.ValidationError(
            get_messege_incorect_obj(
                ("У ингредиентов:", "у ингредиента"),
                amount_incorrect,
                ("некоректное количество", "некоректное количество")
            )
        )
    return ingredient_amount


def add_obj_in_table(
        serialize: serializers.ModelSerializer,
        user: Model,
        obj: Model,
        obj_manager: related_descriptors.ReverseManyToOneDescriptor,
        error_message: str = 'Уже сделано',
) -> Response:
    """Добавить obj в связную таблицу с user"""
    if obj_manager.filter(user=user).exists():
        return Response(
            {'errors': error_message},
            status=status.HTTP_400_BAD_REQUEST
        )
    obj_manager.create(user=user)
    return Response(serialize(obj).data, status=status.HTTP_201_CREATED)


def delete_obj_in_table(
        user: Model,
        obj_manager: related_descriptors.ReverseManyToOneDescriptor,
) -> Response:
    """Удалить obj из связной таблицы с user"""
    model = obj_manager.filter(user=user)
    if not model.exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    model.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def make_content_file(ingredients: list[dict]) -> list[str]:
    """Сформировать содержание списка для отправки"""
    content_file = [
        settings.FIRST_STRING_SHOPPING_LIST.format(today=date.today()), ]
    for num, ingredient in enumerate(ingredients, start=1):
        name, m_unit, amount = ingredient.values()
        content_file.append(
            settings.STRING_SHOPPING_LIST.format(
                number=num,
                name=name,
                amount=amount,
                measurement_unit=m_unit,
            ))
    return content_file


def sent_file(content: any, file_name: str) -> HttpResponse:
    """Отправить содержание ввиде файла"""
    response = HttpResponse(
        content, content_type='text.txt; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    return response
