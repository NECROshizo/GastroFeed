from django.contrib import admin
from django.utils.html import format_html, format_html_join
from .models import (
    Ingredients,
    IngredientsRecipes,
    Recipes,
    Tag
)


EMPTY_VALUE_DISPLAY: str = '-пусто-'


class IngredientsInline(admin.TabularInline):
    model = IngredientsRecipes
    extra = 1
    min_num = 1


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """ Отображение в Админпанели Ингридиентов"""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('name', )
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    """ Отображение в Админпанели Тегов"""
    list_display = ('name', 'show_color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', )
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Цвет')
    def show_color(self, obj: Tag) -> str:
        color_column = format_html(
            '<span style="color:{}">{}</span>',
            obj.color, obj.color
        )
        return color_column


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    """ Отображение в Админпанели Рецептов"""
    list_display = (
        'name', 'show_preview', 'show_tags', 'text',
        'show_ingredients', 'cooking_time',
        'author', 'pub_date',
    )
    search_fields = ('name', 'text', 'author__username', 'tags__name')
    list_filter = ('author', 'cooking_time', 'pub_date',)
    inlines = (IngredientsInline,)
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description='Превью блюда')
    def show_preview(self, obj: Recipes) -> str:
        images_column: str = format_html(
            '<img src="{}" style="max-height: 100px;">',
            obj.image.url
        )
        return images_column

    @admin.display(description='Тэги')
    def show_tags(self, obj: Recipes) -> str:
        tags_column: str = format_html_join(
            ', ', '<span style="color:{}">{}</span>',
            ((tag.color, tag.name) for tag in obj.tags.all())
        )
        return tags_column

    @admin.display(description='Ингредиенты',)
    # TODO слишком много обращений к БД
    def show_ingredients(self, obj: Recipes) -> str:
        ingredients_query_set: list[IngredientsRecipes] = sorted(
            obj.ingredient_in_recipe.all(),
            key=lambda x: -x.amount
        )
        ingredients_column = [
            (
                f'{ingredient_in_recipe.ingredient.name}: '
                f'{ingredient_in_recipe.amount} '
                f'{ingredient_in_recipe.ingredient.measurement_unit}'
            )
            for ingredient_in_recipe in ingredients_query_set
        ]
        return ingredients_column
