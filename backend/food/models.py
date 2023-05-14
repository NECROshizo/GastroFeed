from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator


User = get_user_model()  # TODO заменить на общее
"""
TODO db_comment
"""


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        unique=True,
        validators=[RegexValidator(regex=r'#[A-F0-9]{6}$')]
    )
    slug = models.SlugField(
        max_length=200,
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

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
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

    def __str__(self):
        return self.name


class Recipes(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    image = models.ImageField(
        verbose_name='Готовый результат',
        upload_to='food_images/',
    )
    text = models.TextField('Описание рецепта')
    tags = models.ManyToManyField(
        Tag,
        # on_delete=models.PROTECT,
        related_name='recipes',
        verbose_name='Таг',
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsRecipes',
        related_name='recipes',
        verbose_name='Ингредиенты',
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

    def __str__(self):
        return self.name


class IngredientsRecipes(models.Model):
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
