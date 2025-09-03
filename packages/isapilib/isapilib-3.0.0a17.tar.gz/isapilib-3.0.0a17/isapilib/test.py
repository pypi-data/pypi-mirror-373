import random
import string
import unittest
from datetime import timedelta, datetime
from typing import Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.test import RequestFactory
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from isapilib.api.models import ApiLogs
from isapilib.auth.permissions import IsapilibPermission


class IsapiTestCase(unittest.TestCase):
    interfaz = getattr(settings, 'INTERFAZ_NAME', None)
    auth_data: Union[dict, None] = None
    context = {}

    class AUTHMETHODS:
        JWT = 'jwt'
        OAUTH2 = 'oauth2'
        AUTHTOKEN = 'authtoken'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = APIClient()
        self.factory = RequestFactory()

        if isinstance(self.auth_data, dict):
            user = get_user_model()
            try:
                self.user = user.objects.get(username=self.auth_data['user'])
            except user.DoesNotExist:
                raise Exception(f'El usuario no existe {self.auth_data['user']}')
            self.authenticate()

            factory = RequestFactory()
            request = factory.get('')
            request.user = self.user
            IsapilibPermission.set_current_request(request)

    @property
    def logs(self) -> QuerySet[ApiLogs]:
        if not hasattr(self, '_production_logs'):
            self._production_logs = ApiLogs.objects.filter(interfaz=self.interfaz)
        return self._production_logs

    @staticmethod
    def log(msg):
        now = datetime.now().strftime('%I:%M %p').lower()
        print(msg, now)

    @staticmethod
    def generate_token(length=40):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def authenticate(self):
        auth_method = self.auth_data.get('type', self.AUTHMETHODS.JWT)
        getattr(self, f'auth_{auth_method}')()

    def auth_oauth2(self):
        from oauth2_provider.models import AccessToken, Application

        access_token = AccessToken.objects.filter(user_id=self.user.pk, expires__gt=timezone.now()).first()

        if access_token is None:
            self.application = Application.objects.first()
            access_token = AccessToken.objects.create(
                user=self.user,
                application=self.application,
                token=self.generate_token(),
                expires=timezone.now() + timedelta(days=1),
            )
        else:
            self.application = access_token.application

        self.token = access_token.token
        prefix = self.auth_data.get('token_prefix', 'Bearer')
        self.client.credentials(HTTP_AUTHORIZATION=f'{prefix} ' + self.token)

    def auth_jwt(self):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        prefix = self.auth_data.get('token_prefix', 'Bearer')
        self.client.credentials(HTTP_AUTHORIZATION=f'{prefix} ' + self.token)

    def auth_authtoken(self):
        from rest_framework.authtoken.models import Token

        self.token, _ = Token.objects.get_or_create(user=self.user)
        prefix = self.auth_data.get('token_prefix', 'Token')
        self.client.credentials(HTTP_AUTHORIZATION=f'{prefix} ' + self.token.key)

    def assertResponse(self, request, response, status_code=status.HTTP_200_OK):
        self.assertEqual(
            response.status_code,
            status_code,
            f'\nURL: {response.request['PATH_INFO']}\nREQUEST: {request}\nRESPONSE: {response.content}'
        )
