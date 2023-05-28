from django.conf import settings
from django.contrib import admin
from .models import CookUser


@admin.register(CookUser)
class CookUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email',)
    fields = ('username', 'first_name', 'last_name', 'email',)
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    ordering = ('username',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
