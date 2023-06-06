import django_filters

from recipes.models import Recipe, Tag



class RecipeFilter(django_filters.FilterSet):

    is_favorited = django_filters.NumberFilter(
        method='get_favorited_queryset'
    )
    in_shopping_cart = django_filters.NumberFilter(
        method='get_shopping_cart_queryset'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tag__name',
        to_field_name='name',
        conjoined=True,
    )

    def get_favorited_queryset(self, queryset, name, value):
        user = self.request.user
        if value == 1 and not user.is_anonymous:
            return queryset.filter(favorite_recipe__owner=user)
        return queryset

    def get_shopping_cart_queryset(self, queryset, name, value):
        user = self.request.user
        if value == 1 and not user.is_anonymous:
            return queryset.filter(shopping_recipe__owner=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', ]
