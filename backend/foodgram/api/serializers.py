from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from djoser.serializers import (UserCreateSerializer, UserSerializer,
                                ValidationError)
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import (CurrentUserDefault, ModelSerializer,
                                        SerializerMethodField)

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from users.models import Subscribe
from .utils_serializers import Base64ImageField, Hex2NameColor


User = get_user_model()


class TagSerializer(ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class AuthorRecipesSerializer(ModelSerializer):
    """Сериализ. автора для добавления в рецепты"""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        """Есть ли подписка на этого автора"""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=user, author=obj).exists()


class IngredientAmountSerializer(serializers.Serializer):
    """Сериализ. для добавления amount в ингредиенты"""
    id = serializers.PrimaryKeyRelatedField(
            queryset=Ingredient.objects.all(),)
    amount = serializers.IntegerField(min_value=1,)


class ReadRecipesSerializer(ModelSerializer):
    """Сериализ. для чтения рецептов"""
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = AuthorRecipesSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time',)

    def get_is_favorited(self, obj):
        """Добавлен ли рецепт в список избранного"""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        if Favorite.objects.filter(owner_id=user.pk,
                                   recipe_id=obj.pk).exists():

            return True

        return False

    def get_is_in_shopping_cart(self, obj):
        """Добавлен ли рецепт в список покупок"""
        user = self.context['request'].user
        if user.is_anonymous:

            return False

        if ShoppingCart.objects.filter(owner_id=user.id,
                                       recipe_id=obj.pk).exists():

            return True

        return False


class RecipeSerializer(ModelSerializer):
    """Сериалайзер для модели рецепта"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,)
    author = AuthorRecipesSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time',)

    def create_tags(self, recipe, tags):
        for tag in tags:
            current_tag = get_object_or_404(Tag, id=tag.pk)

            return RecipeTag.objects.create(tag=current_tag, recipe=recipe)

    def create_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            id = ingredient['id'].pk
            amount = ingredient['amount']
            current_ingredient = get_object_or_404(Ingredient, id=id)

            return RecipeIngredient.objects.create(
                ingredient=current_ingredient, recipe=recipe, amount=amount)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tag')
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(recipe, tags)
        self.create_ingredients(recipe, ingredients)

        return recipe

    def to_representation(self, obj):
        data = ReadRecipesSerializer(
            obj, context={'request': self.context.get('request')}).data
        ingredients = data.get('ingredients')
        for ingredient in ingredients:
            ingredient['amount'] = (
                    RecipeIngredient.objects.get(
                        recipe=data['id'], ingredient=ingredient['id']
                        ).amount
                 )

        return data

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        self.create_tags(instance, tags)
        self.create_ingredients(instance, ingredients)

        return instance


class ShoppingCartSerialiser(ModelSerializer):
    """Сериалайзер для списка покупок"""
    recipe = RecipeSerializer(read_only=True, many=True)

    class Meta:
        model = ShoppingCart
        fields = ('recipe',)

    def validate(self, data):
        request = self.context['request']
        recipe_id = self.context.get('view').kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                owner=request.user, recipe=recipe
            ).exists():
                raise ValidationError(
                    'Вы уже добавляли этот рецепт в список покупок.')

        return data


class FavoriteSerialiser(ModelSerializer):
    """Сериализ. для добавления в избранное"""
    recipe = RecipeSerializer(read_only=True, many=True)

    class Meta:
        model = Favorite
        fields = ('id', 'recipe',)
        read_only_fields = ('id',)

    def validate(self, data):
        request = self.context['request']
        recipe_id = self.context.get('view').kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if request.method == 'POST':
            if Favorite.objects.filter(
                owner=request.user, recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже добавляли этот рецепт в избранное.')

        return data


class UserRecipesSerializer(ModelSerializer):
    """Сериализ. с рецептами для модели кастомного юзера"""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', )


class CustomUserSerializer(UserSerializer):
    """Сериализ. кастомного юзера(переопред. Djoser)"""
    recipes = SerializerMethodField('paginated_recipes')
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed',  'recipes', 'recipes_count',)

    def paginated_recipes(self, obj):
        """Пагинация внутри поля рецептов"""
        page_size = self.context['request'].query_params.get(
            'recipes_limit'
        ) or 3
        paginator = Paginator(obj.recipes.all(), page_size)
        page = self.context['request'].query_params.get('page') or 1
        recipes = paginator.page(page)
        serializer = UserRecipesSerializer(recipes, many=True, read_only=True)

        return serializer.data

    def get_is_subscribed(self, obj):
        """Есть ли подписка на этого автора"""
        user = self.context['request'].user
        if user.is_anonymous:

            return False

        return Subscribe.objects.filter(
            user=user, author=obj).exists()

    def get_recipes_count(self, obj):

        return Recipe.objects.filter(author=obj).count()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализ. создания юзера(переопред. Djoser)"""

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password',)

    def validate_username(self, value):
        """Валидация юзернейма."""
        if value.lower() == 'me':
            raise ValidationError('Нельзя использовать логин "me"')

        return value


class SubscribeSerializer(ModelSerializer):
    """Сериализ. подписок на авторов рецетов"""
    author = CustomUserSerializer(read_only=True)
    user = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=CurrentUserDefault()
    )

    class Meta:
        model = Subscribe
        fields = ('author', 'user', )

    def validate_following(self, value):
        """Проверка: юзер подписывается на самого себя."""
        if value == self.context['request'].user:
            raise ValidationError('На себя нельзя подписаться')

        return value

    def validate(self, data):
        """Проверка: юзер повторно подписывается
        на одного и того же автора."""
        request = self.context['request']
        author_id = self.context.get('view').kwargs.get('user_id')
        author = get_object_or_404(User, pk=author_id)
        if request.method == 'POST':
            if Subscribe.objects.filter(
                user=request.user, author=author
            ).exists():
                raise ValidationError(
                    'Вы уже подписаны на этого автора.')

        return data
