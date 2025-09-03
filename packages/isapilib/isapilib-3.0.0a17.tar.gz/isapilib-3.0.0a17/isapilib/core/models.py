import warnings

from django.conf import settings
from django.db import models, router
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from isapilib.api.models import UserAPI  # noqa keep this


class DynamicManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()

        if isinstance(queryset.model._meta.db_table, dict):
            using = router.db_for_write(None)
            version = settings.DATABASES[using]['INTELISIS_VERSION']
            db_table_options = queryset.model._meta.db_table

            try:
                queryset.model._meta.db_table = db_table_options[version]
            except KeyError:
                raise Exception(f'The model {queryset.model} does not have a table for version {version}')

        return queryset


class BaseModel(models.Model):
    objects = DynamicManager()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        for field in self._meta.get_fields():
            if isinstance(field, models.CharField):
                val = str(getattr(self, field.name) or '')
                if val and field.max_length < len(val):
                    setattr(self, field.name, val[:field.max_length])
                    warnings.warn(
                        f'The value of the field "{self.__class__.__name__}.{field.name}" was truncated to {field.max_length} characters')

        using = using or router.db_for_write(None)
        query = self.__class__.objects.using(using).filter(pk=self.pk)

        if self.pk and query.exists():
            fields = update_fields or [
                field.name for field in self._meta.fields
                if field.name != self._meta.pk.name and not isinstance(field, (models.AutoField, models.BigAutoField))
            ]
            values = {field: getattr(self, field) for field in fields}
            query.update(**values)
        else:
            super().save(force_insert, force_update, using, update_fields)

    class Meta:
        abstract = True


class DummyForwardManyToOneDescriptor(ForwardManyToOneDescriptor):
    def __get__(self, instance, cls=None):
        try:
            value = super().__get__(instance, cls)
        except self.field.remote_field.model.DoesNotExist:
            value = getattr(instance, self.field.get_attname())
        return value

    def __set__(self, instance, value):
        if value is not None and not isinstance(value, self.field.remote_field.model._meta.concrete_model):
            setattr(instance, self.field.get_attname(), value)
            instance._state.fields_cache.pop(self.field.name, None)
        else:
            return super().__set__(instance, value)


class DummyForeignKey(models.ForeignKey):
    forward_related_accessor_class = DummyForwardManyToOneDescriptor


def contribute_to_model(model, column, field):
    field.contribute_to_class(model, column)
