from rest_framework import mixins, viewsets
from django.shortcuts import get_object_or_404
from recipes.models import Recipe

class ListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class CreateDestroyViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class ListViewSet(mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    pass
