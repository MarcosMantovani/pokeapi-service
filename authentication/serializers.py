from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.models import User
from users.serializers import GroupSerializer, PermissionSerializer


class TokenExchangeRequestSerializer(serializers.Serializer):
    token = serializers.CharField(
        required=True,
        help_text="Google ID Token" "obtained from Google OAuth2 authentication.",
    )

    class Meta:
        fields = ["token"]
        extra_kwargs = {
            "token": {
                "help_text": "Google ID Token obtained from Google OAuth2 authentication."
            }
        }


class TokenExchangeResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text="Refresh token to be used to obtain a new access token."
    )
    access = serializers.CharField(
        help_text="Access token to be used to authenticate requests."
    )

    class Meta:
        fields = ["refresh", "access"]
        extra_kwargs = {
            "refresh": {
                "help_text": "Refresh token to be used to obtain a new access token."
            },
            "access": {
                "help_text": "Access token to be used to authenticate requests."
            },
        }


class TokenObtainRequestSerializer(serializers.Serializer):
    email = serializers.CharField(
        required=True, help_text="E-mail address to be used to authenticate."
    )
    password = serializers.CharField(
        required=True, help_text="Password to be used to authenticate."
    )

    class Meta:
        fields = ["username", "password"]
        extra_kwargs = {
            "username": {"help_text": "Username to be used to authenticate."},
            "password": {"help_text": "Password to be used to authenticate."},
        }


class TokenObtainResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text="Refresh token to be used to obtain a new access token."
    )
    access = serializers.CharField(
        help_text="Access token to be used to authenticate requests."
    )

    class Meta:
        fields = ["refresh", "access"]
        extra_kwargs = {
            "refresh": {
                "help_text": "Refresh token to be used to obtain a new access token."
            },
            "access": {
                "help_text": "Access token to be used to authenticate requests."
            },
        }


class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text="Refresh token to be used to obtain a new access token."
    )

    class Meta:
        fields = ["refresh"]
        extra_kwargs = {
            "refresh": {
                "help_text": "Refresh token to be used to obtain a new access token."
            }
        }


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField(
        help_text="Access token to be used to authenticate requests."
    )

    class Meta:
        fields = ["access"]
        extra_kwargs = {
            "access": {"help_text": "Access token to be used to authenticate requests."}
        }


class UserRegisterRequestSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        required=True, help_text="Primeiro nome do usuário."
    )
    last_name = serializers.CharField(
        required=True, help_text="Segundo nome (sobrenome) do usuário."
    )
    email = serializers.EmailField(required=True, help_text="E-mail do usuário.")
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Senha do usuário.",
    )

    class Meta:
        fields = ["first_name", "last_name", "email", "password"]

    def validate_password(self, value):
        """
        Valida a senha usando os validadores do Django
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_email(self, value):
        """
        Valida se o email já está em uso
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este e-mail já está em uso.")
        return value


class UserRegisterResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text="Refresh token to be used to obtain a new access token."
    )
    access = serializers.CharField(
        help_text="Access token to be used to authenticate requests."
    )

    class Meta:
        fields = ["refresh", "access"]
        extra_kwargs = {
            "refresh": {
                "help_text": "Refresh token to be used to obtain a new access token."
            },
            "access": {
                "help_text": "Access token to be used to authenticate requests."
            },
        }


class AuthenticatedUserSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(
        many=True, read_only=True, source="user_permissions"
    )

    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ["password", "user_permissions", "polymorphic_ctype"]
