from django.contrib import admin

from recipes.models import Recipe, Tag, Ingredient, Favorite
from users.models import CustomUser


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    search_fields = ('name',)
    autocomplete_fields = ('tag',)


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    search_fields = ('name',)
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'shorttext', 'created',
                    'image', 'cooking_time', 'favorited',)
    inlines = (TagInline, IngredientInline,)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags',)
    empty_value_display = '-пусто-'
    autocomplete_fields = ('author',)

    def favorited(self, obj):

        return Favorite.objects.filter(recipe=obj).count()


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ('username', 'email')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
