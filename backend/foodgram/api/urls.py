from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . views import (RecipesViewSet, TagsViewSet, IngredientsViewSet, ShoppingCartViewSet,
                     FavoriteViewSet, SubscriptionsViewSet, SubscribeViewSet)
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()

router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'recipes/download_shopping_cart', RecipesViewSet, basename='download_shopping_cart')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartViewSet, basename='recipes_shopping_cart')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet, basename='recipes_favorite')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'ingredients', IngredientsViewSet, basename='ingredients')
router.register(r"users/subscriptions", SubscriptionsViewSet, basename='subscribtions')
router.register(r"users/(?P<user_id>\d+)/subscribe", SubscribeViewSet, basename='subscribe')


urlpatterns = [
    path('', include(router.urls), name='api-root'),
    path(r'', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
