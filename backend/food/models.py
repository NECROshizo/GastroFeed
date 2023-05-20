# import user.models as user

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator


MAX_LENGHT_NAME_FOOD: int = 200  # TODO куда??
MAX_LENGHT_COLOR_HEX: int = 7

User = get_user_model()
"""
TODO db_comment
"""


class Tag(models.Model):  # TODO Tags..
    """ Модель тэгов """
    name = models.CharField(
        max_length=MAX_LENGHT_NAME_FOOD,
        verbose_name='Название',
        unique=True,
    )
    color = models.CharField(
        max_length=MAX_LENGHT_COLOR_HEX,
        verbose_name='Цвет',
        unique=True,
        validators=[RegexValidator(regex=r'#[A-F0-9]{6}$')]
    )
    slug = models.SlugField(
        max_length=MAX_LENGHT_NAME_FOOD,
        unique=True,
        validators=[RegexValidator(regex=r'^[-a-zA-Z0-9_]+$')]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name',),
                name='unique_tag'
            ),
        )

    def __str__(self) -> str:
        return self.name


class Ingredients(models.Model):
    """ Модель ингредиентов """
    name = models.CharField(
        max_length=MAX_LENGHT_NAME_FOOD,
        verbose_name='Наименование',
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Ед. измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name',),
                name='unique_ingredient'
            ),
        )

    def __str__(self) -> str:
        return self.name


class Recipes(models.Model):
    """ Модель рецептов """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=MAX_LENGHT_NAME_FOOD,
        verbose_name='Название',
    )
    image = models.ImageField(
        verbose_name='Готовый результат',
        upload_to='food_images/',
    )
    text = models.TextField('Описание рецепта')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Таг',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsRecipes',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    favorited = models.ManyToManyField(
        User,
        related_name='favorit_recipes',
        verbose_name='В избраном',
        blank=True,
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            limit_value=1,
            message='Минимальное время приготовления 1 минута'
        )]
    )
    pub_date = models.DateField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'name', 'pub_date'),
                name='unique_recipes'
            ),
        )

    def __str__(self) -> str:
        return self.name


class IngredientsRecipes(models.Model):
    """ Связующая модель моделей Recipes и Ingredients"""
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Ингредиент',
    )
    recipes = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Рецепт',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиентов',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipes'),
                name='unique_ingredient_to_recipes',
            ),
        )
