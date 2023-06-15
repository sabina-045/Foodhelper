from rest_framework import mixins, viewsets
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework.response import Response
from rest_framework import status
from api.permissions import IsAuthorOnly
from rest_framework.decorators import action


class ListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class CreateDestroyViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    def get_permissions(self):
        if self.action == 'delete':

            return (IsAuthorOnly(),)

        return super().get_permissions()

    def create(self, request, obj_id, model):
        if request.user.is_authenticated:
            recipe = get_object_or_404(Recipe, pk=obj_id)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            model.objects.create(recipe=recipe, user=request.user)

            return Response({'Message': 'Добавление успешно'},
                            status=status.HTTP_201_CREATED)

        return Response({'Errors': 'Пожалуйста, пройдите авторизацию'},
                        status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['delete'], detail=False)
    def delete(self, request, obj_id, model):
        if request.user.is_authenticated:
            recipe = get_object_or_404(Recipe, pk=obj_id)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            model.objects.filter(
                recipe_id=recipe.id,
                user_id=request.user.id).delete()

            return Response({
                'Message': 'Удаление успешно'},
                status=status.HTTP_204_NO_CONTENT
            )

        return Response({'Errors': 'Пожалуйста, пройдите авторизацию'},
                        status=status.HTTP_401_UNAUTHORIZED)
