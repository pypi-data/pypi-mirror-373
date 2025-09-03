from functools import reduce

from django.conf import settings
from django.db import models
from rest_framework.fields import empty, Field, SkipField

from isapilib.core.exceptions import AbortCreationException
from isapilib.external.utilities import get_param_sucursal, get_param_empresa


class CoalesceField(Field):
    def __init__(self, separator=' ', list_source=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_source = list_source
        self.separator = separator
        self.source_provided = False

    def bind(self, field_name, parent):
        self.source_provided = self.source is not None
        return super().bind(field_name, parent)

    def get_attribute(self, instance):
        values = []
        for source in self.list_source:
            for col in source.split('+'):
                if value := getattr(instance, col, None):
                    values.append(value)
                else:
                    values = []
                    break
            if 0 < len(values):
                break

        return self.separator.join(values) if len(values) > 0 else None

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data


class JsonField(Field):
    def __init__(self, json_path=None, return_type=None, prefix=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_path = json_path
        self.return_type = return_type or str
        self.prefix = prefix

    def _get_json_value(self, dictionary):
        real_json_path = self.json_path or self.field_name

        try:
            return reduce(lambda d, key: d[key], real_json_path.split("."), dictionary)
        except (KeyError, TypeError):
            return empty

    def get_value(self, dictionary):
        value = self._get_json_value(dictionary)
        if self.prefix:
            value = f'{self.prefix}{'' if value is empty else value}'
        return value

    def to_internal_value(self, data):
        return self.return_type(data)

    def to_representation(self, value):
        return self.return_type(value)


class SerializerMethodField(Field):
    def __init__(self, method_name_get=None, method_name_set=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method_name_get = method_name_get
        self.method_name_set = method_name_set
        self._value = empty

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        if self.method_name_get is None: self.method_name_get = f'get_{field_name}'
        if self.method_name_set is None: self.method_name_set = f'set_{field_name}'

    def get_attribute(self, instance):
        if method := getattr(self.parent, self.method_name_get, False):
            return method(instance)
        res = super().get_attribute(instance)
        return res

    def get_value(self, dictionary):
        if self._value is not empty: return self._value
        method = getattr(self.parent, self.method_name_set)
        self._value = method(dictionary)
        if self._value is empty or self._value is None:
            try:
                self._value = self.get_default()
            except SkipField:
                self._value = None
        return self._value

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        if issubclass(type(value), models.Model):
            return value.pk
        else:
            return value


class GetOrField(JsonField):
    def __init__(self, model, model_field=None, related=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.model_field = model_field
        self.related = related

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        if self.model_field is None: self.model_field = field_name

    def to_internal_value(self, data):
        instance = self.model.objects.filter(pk=data).first()
        if instance is None: raise self.model.DoesNotExist
        return instance if self.related else instance.pk

    def to_representation(self, value):
        return getattr(value, 'pk', value)

    def get_value(self, dictionary):
        value = super().get_value(dictionary)
        if value is not empty and self.model.objects.filter(**{self.model_field: value}).exists():
            return self.model.objects.filter(**{self.model_field: value}).first().pk
        return empty


class GetOrDefaultField(GetOrField):
    def __init__(self, sucursal_param=None, empresa_param=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sucursal_param = sucursal_param
        self.empresa_param = empresa_param

    def get_value(self, dictionary):
        value = super().get_value(dictionary)
        if value is not empty: return value

        pk = empty
        if self.sucursal_param:
            instance = self.parent.get_instance()
            pk = get_param_sucursal(instance.sucursal, self.sucursal_param)

        if self.empresa_param:
            interfaz = getattr(settings, 'INTERFAZ_NAME', '')
            pk = get_param_empresa(interfaz, self.empresa_param)

        return pk


class GetOrCreateField(GetOrField):
    def __init__(self, method_name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method_name = method_name

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        if self.method_name is None: self.method_name = f'create_{field_name}'

    def get_value(self, dictionary):
        value = super().get_value(dictionary)
        if value is not empty: return value

        try:
            method = getattr(self.parent, self.method_name)
            instance = method(self.parent.initial_data)
            if not isinstance(instance, self.model):
                raise ValueError(f'The function {self.method_name} did not return an instance of the model')
            instance.save()
            return instance.pk
        except AbortCreationException:
            return empty
