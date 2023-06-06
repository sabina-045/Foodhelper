from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField()
    measurement_unit = models.CharField()

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField(
        unique=True,
    )
    color = models.CharField(unique=True)
    slug = models.SlugField(
        unique=True,
        max_length=50,
    )

    def __str__(self) -> str:
        return self.name


class Recipe(CreatedModel):
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=250,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        verbose_name='Фото рецепта',
        upload_to='recipe/images',
    )
    text = models.TextField(
        verbose_name='Рецепт',
        help_text='Напишите здесь рецепт блюда'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Тэг',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        default=1,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created']

    def __str__(self) -> str:
        return self.name


class Favorite(models.Model):
    """Класс избранных рецептов."""
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorite_recipe',
        verbose_name="Избранный рецепт",
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='user_recipe'
        )


class ShoppingCart(models.Model):
    """Класс списка покупок пользователя."""
    owner = models.ForeignKey(
        User,
        verbose_name="Повелитель списка",
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_recipe',
        verbose_name="Рецепт для покупок",
        on_delete=models.CASCADE)


class RecipeIngredient(models.Model):
    """Промежуточный класс рецептов и ингредиентов."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='recipe_infredient',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(default=1)


class RecipeTag(models.Model):
    """Промежуточный класс рецептов и тэгов."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        related_name='recipe_tag',
        on_delete=models.CASCADE,
    )
