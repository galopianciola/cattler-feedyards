from django.conf import settings
from django.utils import translation

from api.models import User


class UserTranslationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response  # siguiente middleware o vista

    def __call__(self, request):
        language = self._resolve_language(request)
        translation.activate(language)
        request.LANGUAGE_CODE = language

        try:
            response = self.get_response(request)
        finally:
            translation.deactivate()

        return response

    def _resolve_language(self, request) -> str:
        user = self._resolve_user(request)
        if user is not None and user.is_authenticated:
            return user.language
        return settings.LANGUAGE_CODE  # anonimo en /auth/token/

    def _resolve_user(self, request) -> User | None:
        if request.user.is_authenticated:
            return request.user

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        key = auth_header.removeprefix("Token ").strip()
        if not key:
            return None

        try:
            return User.objects.get(auth_token__key=key)
        except User.DoesNotExist:
            return None
