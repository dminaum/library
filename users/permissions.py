from rest_framework.permissions import BasePermission


class IsSelfOrAdmin(BasePermission):
    """Доступ к объекту пользователя только себе или админу."""

    def has_object_permission(self, request, view, obj):
        return bool(request.user and (request.user.is_staff or obj == request.user))
