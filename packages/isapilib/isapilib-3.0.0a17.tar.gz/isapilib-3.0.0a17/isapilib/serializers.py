from typing import Any

from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt import serializers as auth_serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from isapilib import validators
from isapilib.core.utilities import get_sucursal_from_request
from isapilib.external.utilities import get_sucursal, get_uen, get_almacen
from isapilib.fields import SerializerMethodField
from isapilib.mixin.instance import InstanceMixIn
from isapilib.models import Venta, Empresa, Vin


class BaseVentaSerializer(InstanceMixIn, serializers.ModelSerializer):
    sucursal = SerializerMethodField()
    empresa = SerializerMethodField()
    almacen = SerializerMethodField()
    uen = SerializerMethodField()
    cliente = serializers.CharField()

    class Meta:
        model = Venta
        fields = '__all__'
        read_only_fields = ['mov', 'mov_id']

    def set_sucursal(self, data):
        instance: Venta = self.get_instance()
        request = self.context.get('request')
        return get_sucursal(mov=instance.mov, sucursal=get_sucursal_from_request(request))

    def set_empresa(self, data):
        return Empresa.objects.all().first()

    def set_almacen(self, data):
        instance: Venta = self.get_instance()
        return get_almacen(mov=instance.mov, sucursal=instance.sucursal.pk)

    def set_uen(self, data):
        instance: Venta = self.get_instance()
        return get_uen(mov=instance.mov, sucursal=instance.sucursal.pk)

    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)

        if hasattr(self, 'set_vin'):
            vin: Vin = self.set_vin(data)
            if not isinstance(vin, Vin):
                raise ValueError(f'The function get_vin did not return an instance of VIN')
            internal_value['servicio_serie'] = vin.vin
            internal_value['servicio_modelo'] = vin.modelo
            internal_value['servicio_articulo'] = vin.articulo
            internal_value['servicio_placas'] = vin.placas
            internal_value['servicio_kms'] = vin.km
            internal_value['servicio_descripcion'] = vin.color_exterior or 'NEGRO'
            internal_value['servicio_identificador'] = vin.color_exterior or 'NEGRO'

        return internal_value


class BaseCitaSerializer(BaseVentaSerializer):
    mov = serializers.CharField(default='Cita Servicio')
    agente = serializers.CharField()
    fecha_requerida = serializers.CharField()
    hora_recepcion = serializers.CharField()

    class Meta:
        model = Venta
        fields = '__all__'
        read_only_fields = ['mov', 'mov_id']
        validators = [
            validators.DateAfterTodayValidator(),
            validators.NoDuplicateAppointmentsValidator(),
        ]


class TokenObtainPairSerializer(auth_serializers.TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh_token"] = str(refresh)
        data["access_token"] = str(refresh.access_token)
        data["expires_in"] = int(refresh.access_token.lifetime.total_seconds())

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
