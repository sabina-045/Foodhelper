from django.db.models import Sum
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
from .filters import RecipeFilter, SearchFilter
from .mixins import CreateDestroyViewSet, ListRetrieveViewSet, ListViewSet
from .pagination import CustomPagination
from .permissions import AuthorOrAdminOrReadOnly, ReadOrAdminOnly, IsAuthorOnly
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer)


User = get_user_model()


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrAdminOrReadOnly, )
    filter_backends = (SearchFilter)
    filterset_class = RecipeFilter
    search_fields = ('^ingredients__name',)

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
        ingredients_list = RecipeIngredient.objects.filter(
            recipe_id__in=recipe_id).values_list(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            Sum('amount'))
        for ingredient in ingredients_list:
            name = ingredient[0]
            measure = ingredient[1]
            amount = ingredient[2]
            response.write(f'{name}: {amount} {measure} \n')

        return response


class ShoppingCartViewSet(CreateDestroyViewSet):
    serializer_class = ShoppingCartSerializer

    def create(self, request, obj_id):
        return super().create(request, obj_id, ShoppingCart)

    def delete(self, request, obj_id):
        return super().delete(request, obj_id, ShoppingCart)


class FavoriteViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteSerializer

    def create(self, request, obj_id):
        return super().create(request, obj_id, Favorite)

    def delete(self, request, obj_id):
        return super().delete(request, obj_id, Favorite)


class TagsViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOrAdminOnly, )
    pagination_class = None


class IngredientsViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (ReadOrAdminOnly, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    pagination_class = None


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

    def create(self, request, obj_id):
        if request.user.is_authenticated:
            author = get_object_or_404(User, pk=obj_id)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=request.user, author=author)

            return Response({'Message': 'Добавление успешно'},
                            status=status.HTTP_201_CREATED)

        return Response({'Errors': 'Пожалуйста, пройдите авторизацию'},
                        status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, obj_id):
        if request.user.is_authenticated:
            author = get_object_or_404(User, pk=obj_id)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.filter(
                author_id=author.id,
                user_id=request.user.id).delete()

            return Response({
                'Message': 'Удаление успешно'},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response({'Errors': 'Пожалуйста, пройдите авторизацию'},
                        status=status.HTTP_401_UNAUTHORIZED)
