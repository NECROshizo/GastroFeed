from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
User = get_user_model()


class Tag(models.Model):
    """
    Модель тегов
    ...
    Attributes
    ----------
    name  :  str
        Название тега.(Завтрак)
    color  :  str
        Цвет в формате HEX.(#F3F366)
    slug  :  str
        Слаг для Тега. (breakfast)
    """
    name = models.CharField(
        'Название',
        max_length=settings.MAX_LENGHT_NAME_FOOD,
        unique=True,
        db_comment='Отображаемое название тега',
        help_text='Придумайте название тега',
    )
    color = models.CharField(
        'Цвет',
        max_length=settings.MAX_LENGHT_COLOR_HEX,
        unique=True,
        db_comment='Цвет в HEX-формате',
        help_text='Используйте цвет в формате HEX',
        validators=[RegexValidator(
            regex=settings.PATTERN_COLORS_TAG,
            message=settings.MESSAGE_COLORS_TAG,
        )]
    )
    slug = models.SlugField(
        'Слаг',
        max_length=settings.MAX_LENGHT_NAME_FOOD,
        unique=True,
        db_comment='Slug для цвета',
        help_text='Используйте slug состаящий из '
                  'латинских букв, цифр и символа _',
        validators=[RegexValidator(
            regex=settings.PATTERN_SLUG_TAG,
            message=settings.MESSAGE_SLUG_TAG,
        )]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=('name',),
                name='unique_tag'
            ),
        )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """
    Модель ингредиентов
    ...
    Attributes
    ----------
    name  :  str
        Название ингредиента.(Морковь)
    measurement_unit  :  str
        Единицы измерения (г.)
    """
    name = models.CharField(
        'Наименование',
        max_length=settings.MAX_LENGHT_NAME_FOOD,
        db_comment='Название ингредиента',
        help_text='Придумайте название ингредиента',
    )
    measurement_unit = models.CharField(
        'Ед. измерения',
        max_length=20,
        db_comment='Ед.измерения ингредиента',
        help_text='Обозначте ед. измерения ингредиента',
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


class Recipe(models.Model):
    """
    Модель рецептов
    ...
    Attributes
    ----------
    author  :  int
        Автор рецепта,
        по fk с моделью CookUser(AbstractUser)
        Поля:   userman, email, first_name, last_name
                subscriptions
    name : str
        Название рецепта
    image  : str
        Изображение рецепта
    text : str
        Описание рецепта
    tags : int
        Теги рецепта,
        по m2m с моделью Tag
        Поля:   name, color, slug,
    ingredients : int
        Используемые ингредиенты,
        по m2m с моделью Ingredient
        Поля Ingredient:                name, measurement_unit
        Доп. поля IngredientsRecipes:   amount
    favorited : int
        Те кто добавили рецепт в избранное,
        по fk с моделью CookUser(AbstractUser)
        Поля:   userman, email, first_name, last_name
                subscriptions
    shopping_cart : int
        Те кто добавили рецепт в корзину,
        по fk с моделью CookUser(AbstractUser)
        Поля:   userman, email, first_name, last_name
                subscriptions
    cooking_time : int
        Время приготовления
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        db_comment='Автор рецепта',
        help_text='Выберете автора',
    )
    name = models.CharField(
        max_length=settings.MAX_LENGHT_NAME_FOOD,
        verbose_name='Название',
    )
    image = models.ImageField(
        'Готовый результат',
        upload_to='food_images/',
        db_comment='Изображение рецепта',
        help_text='Выберете илюстрацию рецепта',
    )
    text = models.TextField(
        'Описание рецепта',
        db_comment='Инструкция приготовления',
        help_text='Опишите приготовление рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
        db_comment='Теги рецепта',
        help_text='Обозначьте теги рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsRecipes',
        related_name='recipes',
        verbose_name='Ингредиенты',
        db_comment='Ингредиенты',
        help_text='Выберете ингредиенты',
    )
    favorited = models.ManyToManyField(
        User,
        through='Favorite',
        related_name='recipes_favorit',
        verbose_name='В избраном',
        db_comment='Добавившие в избранное',
        help_text='Добавте в избранное',
        blank=True,
    )
    shopping_cart = models.ManyToManyField(
        User,
        through='ShoppingCart',
        related_name='recipes_shopping_cart',
        verbose_name='В корзине',
        db_comment='Добавившие в корзину',
        help_text='Добавте в корзину',
        blank=True,
    )
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        db_comment='Время приготовления',
        help_text='Обозначьте время приготовления',
        validators=[MinValueValidator(
            limit_value=1,
            message='Минимальное время приготовления 1 минута'
        )]
    )
    pub_date = models.DateField(
        'Дата создания',
        db_comment='Дата добавления рецепта(авто)',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.name


class IngredientsRecipes(models.Model):
    """
    Связующая модель моделей Recipe и Ingredient
    ...
    Attributes
    ----------
    ingredients : int
        Используемые ингредиенты,
        по fk с моделью Ingredient
        Поля:    name, measurement_unit
    recipe : int
        Рецепты где есть ингредиент,
        по fk с моделью Recipe
        Поля:   author, name, image, text, tags, ingredients,
                favorited, shopping_cart, cooking_time
    amount : int
        Количество ингредиентов в рецепте
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipe',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
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
        ordering = ['recipe']
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredients_recipes',
            ),
        )


class Favorite(models.Model):
    """
    Модель избранного
    ...
    Attributes
    ----------
    user  :  int
        Добавивший в избранное,
        по fk с моделью CookUser(AbstractUser)
        Поля:   userman, email, first_name, last_name
                subscriptions
    recipe : int
        Рецепт в избранном,
        по fk с моделью Recipe
        Поля:   author, name, image, text, tags, ingredients,
                favorited, shopping_cart, cooking_time
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorit_user_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorit_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Добавил в избранное'
        verbose_name_plural = 'Добавили в избранное'
        ordering = ['user']
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorit',
            ),
        )


class ShoppingCart(models.Model):
    """
    Модель корзины
        ...
    Attributes
    ----------
    user  :  int
        Добавивший в корзину,
        по fk с моделью CookUser(AbstractUser)
        Поля:   userman, email, first_name, last_name
                subscriptions
    recipe : int
        Рецепт в корзине,
        по fk с моделью Recipe
        Поля:   author, name, image, text, tags, ingredients,
                favorited, shopping_cart, cooking_time
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoping_card_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoping_card_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Добавил в корзину'
        verbose_name_plural = 'Добавили в корзину'
        ordering = ['user']
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shoping_card',
            ),
        )
