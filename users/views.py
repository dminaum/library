from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import IsSelfOrAdmin
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


@extend_schema(
    tags=["Auth"],
    auth=None,
    examples=[
        OpenApiExample(
            "Пример регистрации",
            value={
                "username": "user1",
                "email": "u1@example.com",
                "password": "StrongPassw0rd!",
                "first_name": "U",
                "last_name": "One",
                "phone": "+34999",
            },
            request_only=True,
        )
    ],
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


@extend_schema(tags=["Users"], summary="Профиль текущего пользователя")
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "list":
            return [permissions.IsAdminUser()]
        if self.action in ("retrieve",):
            return [IsSelfOrAdmin()]
        if self.action == "me":
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(tags=["Users"], summary="Текущий пользователь")
    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
