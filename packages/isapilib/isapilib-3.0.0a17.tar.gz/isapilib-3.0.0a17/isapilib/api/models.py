from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import connections
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from encrypted_model_fields.fields import EncryptedCharField

from isapilib.core.exceptions import SepaException
from isapilib.core.utilities import is_test


class ConnectionAPI(models.Model):
    user = models.CharField(max_length=40)
    password = EncryptedCharField(max_length=40)
    host = models.CharField(max_length=40)
    port = models.CharField(max_length=80, null=True, blank=True)
    nombre_db = models.CharField(max_length=80)
    empresa = models.CharField(max_length=80, null=True, blank=True)
    version = models.IntegerField(default=6000)
    allow_test = models.BooleanField(default=False)
    extra_data = models.JSONField(default=dict)

    def get_name(self):
        return f'external-{self.pk}'

    def get_database_configuration(self):
        if self.pk: self.refresh_from_db()
        return {
            'ENGINE': 'mssql',
            'NAME': getattr(self, 'nombre_db', ''),
            'USER': getattr(self, 'user', ''),
            'PASSWORD': getattr(self, 'password', ''),
            'HOST': getattr(self, 'host', ''),
            'PORT': getattr(self, 'port', ''),
            'INTELISIS_VERSION': getattr(self, 'version', ''),
            'TIME_ZONE': None,
            'CONN_HEALTH_CHECKS': None,
            'CONN_MAX_AGE': None,
            'ATOMIC_REQUESTS': None,
            'AUTOCOMMIT': True,
            'OPTIONS': settings.DATABASES['default'].get('OPTIONS')
        }

    def create_connection(self):
        name = self.get_name()

        if name in connections.databases:
            connections.databases[name] = self.get_database_configuration()
            return name

        if is_test() and not self.allow_test:
            raise SepaException(f'Test is not allowed at this connection {self.pk}')

        connections.databases[name] = self.get_database_configuration()

        return name

    def verify_connection(self):
        name = 'test_connection'
        connections.databases[name] = self.get_database_configuration()

        try:
            connection = connections[name]
            cursor = connection.cursor()
            cursor.execute('SELECT 1')
            return True, None
        except Exception as e:
            return False, str(e)

    class Meta:
        db_table = 'isapilib_connectionapi'
        unique_together = ('host', 'port', 'nombre_db')
        ordering = ['host', 'port', 'id']


class BranchAPI(models.Model):
    connection = models.ForeignKey(ConnectionAPI, on_delete=models.CASCADE, related_name='branches')
    sucursal = models.IntegerField()
    gwmbac = models.CharField(max_length=100, null=True, blank=True, unique=True)
    users = models.ManyToManyField(UserAPI,  related_name="permissions")

    def check_permissions(self, user):
        if user.is_anonymous:
            raise SepaException(f'Anonymous user is not allowed at this connection {self.pk}')
        return self.permissions.filter(user=user).exists()

    class Meta:
        db_table = 'isapilib_branchapi'
        ordering = ['connection', 'id']


class UserProfileManager(BaseUserManager):
    pass


class UserAPI(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    is_superuser = models.BooleanField(default=False)
    branch = models.ForeignKey(BranchAPI, on_delete=models.CASCADE, null=True, blank=True, related_name='users')

    USERNAME_FIELD = 'username'

    objects = UserProfileManager()

    class Meta:
        db_table = 'isapilib_userapi'
        ordering = ['username', 'id']


class ApiLogs(models.Model):
    user = models.ForeignKey(UserAPI, on_delete=models.CASCADE, null=True, blank=True, related_name='logs')
    tipo = models.CharField(max_length=120)
    header = models.TextField()
    request = models.TextField()
    response = models.TextField()
    status = models.IntegerField(null=True)
    url = models.TextField()
    interfaz = models.CharField(max_length=120)
    fecharegistro = models.DateTimeField(auto_now=True)
    response_time = models.IntegerField(default=0)

    class Meta:
        db_table = 'api_logs'
        ordering = ['-fecharegistro']


@receiver(post_save, sender=ApiLogs)
def delete_old_logs(sender, instance, **kwargs):
    interfaz = getattr(settings, 'INTERFAZ_NAME', '')
    max_number_logs = getattr(settings, 'MAX_NUMBER_LOGS', 500)
    if max_number_logs < ApiLogs.objects.count():
        logs_to_delete = ApiLogs.objects.filter(interfaz=interfaz).order_by('-fecharegistro')[max_number_logs:]
        list(map(lambda i: i.delete(), logs_to_delete))
