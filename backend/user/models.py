from django.contrib.auth.models import AbstractUser
from django.db import models
# from food.models import Recipes
# import food.models as food


class CookUser(AbstractUser):
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
    )

    # username = models.CharField(
    #     'Псевдоним пользователя',
    #     max_length=150,
    #     unique=True,
    #     help_text=(
    #         'Обязателен к заполнению.'
    #         'Используйти только буквы, цифры и @/./+/-/_. '
    #     ),
    #     validators=[super().username_validator],
    #     error_messages={
    #         "unique": "Пользователь с таким именем уже существует.",
    #     },
    # )
    first_name = models.CharField('Имя', max_length=150,)
    last_name = models.CharField('Фамилия', max_length=150,)
    # password = models.CharField('Пароль', max_length=150,)
    # recipies = models.ManyToManyField(
    #     Recipes,
    #     related_name='user',
    #     blank=True,
    #     verbose_name='Рецепты',
    # )
    subscriptions = models.ManyToManyField(
        'CookUser',
        related_name='user',
        blank=True,
        verbose_name='Подписки',
    )
