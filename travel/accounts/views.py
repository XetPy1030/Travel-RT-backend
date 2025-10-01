from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LogoutSerializer, UserCreateSerializer, UserSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=LogoutSerializer,
        responses={
            205: OpenApiResponse(description="Успешный выход из системы"),
            400: OpenApiResponse(description="Неверный токен обновления"),
            401: OpenApiResponse(description="Ошибка аутентификации"),
        },
        description="Выход пользователя из системы путем блокировки токена обновления",
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=status.HTTP_205_RESET_CONTENT)


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer

    @extend_schema(
        request=UserCreateSerializer,
        responses={
            201: UserCreateSerializer,
            400: OpenApiResponse(description="Неверные данные"),
        },
        description="Создание нового пользователя",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    @extend_schema(
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Ошибка аутентификации"),
        },
        description="Получение или обновление профиля аутентифицированного пользователя",
    )
    def get_object(self):
        return self.request.user
