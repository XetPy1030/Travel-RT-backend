from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import UserSerializer, LogoutSerializer, UserCreateSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=LogoutSerializer,
        responses={
            205: OpenApiResponse(description="Successfully logged out"),
            400: OpenApiResponse(description="Invalid refresh token"),
            401: OpenApiResponse(description="Authentication failed")
        },
        description="Logout a user by blacklisting their refresh token"
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
            400: OpenApiResponse(description="Invalid data")
        },
        description="Create a new user account"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    
    @extend_schema(
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description="Authentication failed")
        },
        description="Retrieve or update the authenticated user's profile"
    )
    def get_object(self):
        return self.request.user
