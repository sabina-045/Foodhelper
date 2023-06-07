from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOrAdminOnly(BasePermission):
    """Доступ админу к действиям над объектом."""
    def has_permission(self, request, view):

        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_staff))


class AuthorOrAdminOrReadOnly(BasePermission):
    """Разрешение всем пользователям просматривать объект.
    Разрешение только владельцу и админу редактировать и удалять объект."""
    def has_permission(self, request, view):

        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):

        return (request.method in SAFE_METHODS
                or obj.author == request.user
                or request.user.is_staff)


class IsAuthorOnly(BasePermission):
    def has_object_permission(self, request, view, obj):

        return obj.author == request.user
