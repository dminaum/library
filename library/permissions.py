from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Чтение всем, запись только is_staff (админ/библиотекарь)."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        u = request.user
        return bool(u and (u.is_staff or obj.user_id == u.id))
