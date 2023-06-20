import django_filters
# from rest_framework import filters
from django.contrib.auth import get_user_model

from recipes.models import Recipe, Tag, Ingredient

User = get_user_model()


# class SearchFilter(filters.SearchFilter):
#     SEARCH_PARAM = 'name'
class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_favorited = django_filters.NumberFilter(
        method='get_favorited_queryset'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='get_shopping_cart_queryset'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', ]

    def get_favorited_queryset(self, queryset, name, value):
        user = self.request.user
        if value == 1 and not user.is_anonymous:

            return queryset.filter(favorite_recipe__user=user)

        return queryset

    def get_shopping_cart_queryset(self, queryset, name, value):
        user = self.request.user
        if value == 1 and not user.is_anonymous:

            return queryset.filter(shopping_recipe__user=user)

        return queryset
