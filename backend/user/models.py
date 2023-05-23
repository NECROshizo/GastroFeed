from django.contrib.auth.models import AbstractUser
from django.db import models


class CookUser(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', )

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

    subscriptions = models.ManyToManyField(
        'CookUser',
        through='Subscriptions',
        related_name='user',
        blank=True,
        verbose_name='Подписки',
    )

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    # def __str__(self):
    #     return f'{self.get_full_name} aka {self.username}'


class Subscriptions(models.Model):
    auther = models.ForeignKey(
        CookUser,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name='Автор',
    )
    subscriber = models.ForeignKey(
        CookUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчики',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписка'
        constraints = (
            models.UniqueConstraint(
                fields=('auther', 'subscriber'),
                name='unique_subscriptions',
            ),
            models.CheckConstraint(
                check=~models.Q(auther=models.F('subscriber')),
                name='На себя нельзя',)
        )
