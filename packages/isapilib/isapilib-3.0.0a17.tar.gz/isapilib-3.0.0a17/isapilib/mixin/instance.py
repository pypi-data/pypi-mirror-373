import copy
from typing import TypeVar

from django.db import models
from rest_framework.fields import empty, SkipField

SubModel = TypeVar('SubModel', bound=models.Model)


class InstanceMixIn:

    @property
    def got_data(self):
        if not hasattr(self, '_got_data'):
            self._got_data = {}
        return self._got_data

    def got(self, name, fun):
        def wrapper(*args, **kwargs):
            data = fun(*args, **kwargs)
            if data is not empty:
                self.got_data[name] = data
            return data

        return wrapper

    def get_fields(self):
        wrapper_fields = copy.deepcopy(self._declared_fields)

        for name, field in wrapper_fields.items():
            get_value_method = self.got(name, getattr(field, 'get_value'))
            setattr(field, 'get_value', get_value_method)
            try:
                self.got_data[name] = field.get_default()
            except SkipField:
                pass

        return wrapper_fields

    def get_instance(self):
        model = self.Meta.model
        instance = model()
        for name, data in self.got_data.items():
            field = self.fields[name]
            value = field.to_internal_value(data)
            setattr(instance, name, value)
        return instance
