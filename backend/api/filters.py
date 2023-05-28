from django_filters import FilterSet, filters
from food.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        # lookup_type='in',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
        )
