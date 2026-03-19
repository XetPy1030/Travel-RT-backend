import secrets

from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed


class ParserServicePrincipal:
    is_authenticated = True
    is_anonymous = False

    def __str__(self):
        return "parser-service"


class ParserBearerAuthentication(BaseAuthentication):
    keyword = b"bearer"

    def authenticate_header(self, request):
        return "Bearer"

    def authenticate(self, request):
        expected_token = settings.PARSER_SERVICE_TOKEN
        if not expected_token:
            raise AuthenticationFailed("Parser token is not configured.")

        auth = get_authorization_header(request).split()
        if not auth:
            raise AuthenticationFailed("Authorization header is required.")
        if auth[0].lower() != self.keyword:
            raise AuthenticationFailed("Invalid authorization scheme.")
        if len(auth) == 1:
            raise AuthenticationFailed("Token is required.")
        if len(auth) > 2:
            raise AuthenticationFailed("Invalid Authorization header format.")

        try:
            token = auth[1].decode("utf-8")
        except UnicodeError as exc:
            raise AuthenticationFailed("Invalid token encoding.") from exc

        if not secrets.compare_digest(token, expected_token):
            raise AuthenticationFailed("Invalid parser token.")

        return ParserServicePrincipal(), token
