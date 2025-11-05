from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    AuthenticatedUserSerializer,
    TokenExchangeRequestSerializer,
    TokenExchangeResponseSerializer,
    TokenObtainRequestSerializer,
    TokenObtainResponseSerializer,
    TokenRefreshRequestSerializer,
    TokenRefreshResponseSerializer,
    UserRegisterRequestSerializer,
    UserRegisterResponseSerializer,
)

User = get_user_model()


class GoogleTokenExchangeView(APIView):
    def post(self, request, *args, **kwargs):
        token = request.data.get("token")
        try:
            # Verifica o token do Google
            idinfo = id_token.verify_oauth2_token(token, requests.Request())

            if "email" not in idinfo:
                return Response(
                    {"error": "Google Authentication Failed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            email = idinfo["email"]
            user, created = User.objects.get_or_create(
                email=email, defaults={"username": email}
            )

            if created:
                # Aqui, você pode definir mais campos do usuário, se necessário,
                user.first_name = idinfo.get("given_name")
                user.last_name = idinfo.get("family_name")
                user.save()

            if not user.is_active:
                return Response(
                    {"error": "User is currently inactive."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Gerar JWT para o usuário
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            )

        except ValueError:
            # Token inválido
            return Response(
                {"error": "Invalid Google Authentication Token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(responses={200: TokenExchangeResponseSerializer})
@extend_schema(
    request=TokenExchangeRequestSerializer, responses=TokenExchangeResponseSerializer
)
class TokenExchangeViewSet(viewsets.ViewSet):

    @extend_schema(
        request=TokenExchangeRequestSerializer,
        responses=TokenExchangeResponseSerializer,
    )
    def create(self, request, *args, **kwargs):
        view = GoogleTokenExchangeView.as_view()
        return view(request._request, *args, **kwargs)


@extend_schema(responses={200: TokenObtainResponseSerializer})
@extend_schema(
    request=TokenObtainRequestSerializer, responses=TokenObtainResponseSerializer
)
class TokenObtainPairViewSet(viewsets.ViewSet):

    def create(self, request, *args, **kwargs):
        view = TokenObtainPairView.as_view()
        return view(request._request, *args, **kwargs)


@extend_schema(responses={200: TokenRefreshResponseSerializer})
@extend_schema(
    request=TokenRefreshRequestSerializer, responses=TokenRefreshResponseSerializer
)
class TokenRefreshViewSet(viewsets.ViewSet):

    def create(self, request, *args, **kwargs):
        view = TokenRefreshView.as_view()
        return view(request._request, *args, **kwargs)


class AuthenticatedUserView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            return Response(
                AuthenticatedUserSerializer(user).data, status=status.HTTP_200_OK
            )

        return Response(
            {"error": "User is not authenticated."}, status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(responses={200: AuthenticatedUserSerializer})
class AuthenticatedUserViewSet(viewsets.ViewSet):

    @action(detail=False, methods=["get"])
    def user(self, request, *args, **kwargs):
        view = AuthenticatedUserView.as_view()
        return view(request._request, *args, **kwargs)


class UserRegisterView(APIView):
    """
    Endpoint público para registro de novos usuários.
    Cria um usuário e retorna tokens JWT.
    """

    permission_classes = [AllowAny]  # Público, sem autenticação necessária

    @extend_schema(
        request=UserRegisterRequestSerializer,
        responses={201: UserRegisterResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = UserRegisterRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Cria o usuário usando o UserManager
            user = User.objects.create_user(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
            )

            # Gera tokens JWT para o novo usuário
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=UserRegisterRequestSerializer,
    responses={201: UserRegisterResponseSerializer},
)
class UserRegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]  # Público, sem autenticação necessária

    def create(self, request, *args, **kwargs):
        view = UserRegisterView.as_view()
        return view(request._request, *args, **kwargs)
