from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscribe
from .filters import RecipeFilter
from .mixins import CreateDestroyViewSet, ListRetrieveViewSet, ListViewSet
from .pagination import CustomPagination
from .permissions import AuthorOrAdminOrReadOnly, ReadOrAdminOnly, IsAuthorOnly
from .serializers import (CustomUserSerializer, FavoriteSerialiser,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerialiser, SubscribeSerializer,
                          TagSerializer)


User = get_user_model()


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, )
    filterset_class = RecipeFilter

    def perform_create(self, serializer):

        return serializer.save(author=self.request.user)

    @action(detail=False, permission_classes=(IsAuthorOnly,))
    def download_shopping_cart(self, request):
        """Дополнительный эндпойнт: загрузить список покупок"""
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment;filename="shopping_cart.txt"'
        )
        response.write(f'Я {request.user}\n')
        response.write('И это мой список покупок:\n \n')

        recipe_id = ShoppingCart.objects.values_list('recipe_id')
        empty_dict = {}
        for recipe in recipe_id:
            ing_amount = RecipeIngredient.objects.filter(
                    recipe_id__in=recipe).values_list(
                    'ingredient__name', 'amount',
                    )
            ing_amount = dict(ing_amount)
            for key, value in ing_amount.items():
                if key in empty_dict:
                    empty_dict.update([(key, value + empty_dict[key])])
                else:
                    empty_dict.update([(key, value)])
        for ing, amount in empty_dict.items():
            measurement_unit = Ingredient.objects.filter(name=ing).values_list(
                'measurement_unit', flat=True
                ).first()

            response.write(f'{ing}: {amount} {measurement_unit} \n')

        return response


class ShoppingCartViewSet(CreateDestroyViewSet):
    serializer_class = ShoppingCartSerialiser

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))
            if ShoppingCart.objects.filter(
                recipe_id=recipe.id,
                owner_id=self.request.user.id
            ).exists():

                return Response({
                    'Errors': 'Этот рецепт уже есть в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save(recipe_id=recipe.id, owner_id=self.request.user.id)

            return Response({'Message': 'рецепт добавлен в список'},
                            status=status.HTTP_201_CREATED)

        return Response({'Errors': 'Пожалуйста, пройдите авторизацию'},
                        status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['delete'], detail=False)
    def delete(self, request, recipe_id):
        if request.user.is_authenticated:
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            shopping_cart = ShoppingCart.objects.filter(
                recipe_id=recipe.id,
                owner_id=self.request.user.id)
            if not shopping_cart:

                return Response({
                    'Errors': 'Этого рецепта нет в вашем списке'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shopping_cart.delete()

            return Response({
                'Message': 'рецепт успешно удален из списка'},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response({'Errors': 'Пожалуйста, пройдите авторизацию'},
                        status=status.HTTP_401_UNAUTHORIZED)


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerialiser

    def perform_create(self, serializer):
        recipe = get_object_or_404(Recipe, pk=self.kwargs.get('recipe_id'))

        return serializer.save(recipe_id=recipe.id,
                               owner_id=self.request.user.id)

    @action(methods=['delete'], detail=False)
    def delete(self, request, recipe_id):
        if request.user.is_authenticated:
            recipe = get_object_or_404(Recipe, pk=recipe_id)
            favorite = Favorite.objects.filter(
                recipe_id=recipe.id,
                owner_id=self.request.user.id)
            if not favorite:

                return Response({
                    'Errors': 'Этого рецепта нет в ваших подписках'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite.delete()

            return Response({
                'Message': 'рецепт успешно удален из избранного'},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response({'Errors': 'Пожалуйста, пройдите авторизацию'},
                        status=status.HTTP_401_UNAUTHORIZED)


class TagsViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOrAdminOnly, )


class IngredientsViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AuthorOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)


class SubscriptionsViewSet(ListViewSet):
    """Список авторов с рецептами, на котрых подписан юзер"""
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOnly, )

    def get_queryset(self):

        return User.objects.filter(following__user=self.request.user)


class SubscribeViewSet(CreateDestroyViewSet):
    """Создание и удаление подписки на автора."""
    serializer_class = SubscribeSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        """Создание подписки на автора."""
        author = get_object_or_404(User, pk=self.kwargs.get('user_id'))

        return serializer.save(author_id=author.id,
                               user_id=self.request.user.id)

    @action(methods=['delete'], detail=False)
    def delete(self, request, user_id):
        """Отписка от автора."""
        if request.user.is_authenticated:
            author = get_object_or_404(User, pk=user_id)
            subscribe = Subscribe.objects.filter(author_id=author.id,
                                                 user=request.user)
            if not author:

                return Response({'Errors': 'Такого автора не существует'},
                                status=status.HTTP_404_NOT_FOUND)

            if not subscribe:

                return Response({
                    'Errors': 'Вы не были подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscribe.delete()

            return Response({
                'Message': 'Вы успешно отписались от данного автора'},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response({'Errors': 'Пожалуйста, пройдите авторизацию'},
                        status=status.HTTP_401_UNAUTHORIZED)
