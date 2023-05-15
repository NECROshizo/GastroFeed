from django.contrib import admin
from .models import CookUser


@admin.register(CookUser)
class CookUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',)
    fields = ('username', 'first_name', 'last_name', 'email',)
    search_fields = ('username', 'email', 'get_full_name',)
    list_filter = ('username', 'first_name', 'last_name',)
    ordering = ('username',)
    empty_value_display = '-пусто-'
