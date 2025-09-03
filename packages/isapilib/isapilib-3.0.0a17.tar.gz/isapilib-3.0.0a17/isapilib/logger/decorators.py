import time

from django.conf import settings
from django.http import JsonResponse
from django.utils.module_loading import import_string
from rest_framework.request import Request

from isapilib.core.decorators import safe_method

try:
    insert_log = import_string(settings.INSERT_LOG_FUNCTION)
except Exception:
    from isapilib.logger.utilities import insert_log


def logger_method(tipo, interfaz=None, log_all=True):
    interfaz = interfaz or getattr(settings, 'INTERFAZ_NAME', '')

    def decorador(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            request = next((arg for arg in args if isinstance(arg, Request)), None)

            try:
                response: JsonResponse = func(*args, **kwargs)
                end = time.time()
                if (hasattr(response, 'status_code') and response.status_code not in range(200, 300)) or log_all:
                    response_time = (end - start) * 1000
                    insert_log(request=request, response=response, interfaz=interfaz, tipo=tipo, time=response_time)
                return response
            except Exception as e:
                insert_log(request=request, response=str(e), interfaz=interfaz, tipo=tipo)
                raise e

        return wrapper

    return decorador


def logger(tipo, interfaz=None, log_all=True):
    interfaz = interfaz or getattr(settings, 'INTERFAZ_NAME', '')

    def class_decorator(cls):
        method_names = ['get', 'post', 'put', 'delete']
        for method_name in method_names:
            if not hasattr(cls, method_name): continue
            method = getattr(cls, method_name)
            log_tipo = f'{tipo} {method_name.upper()}'
            setattr(cls, method_name, logger_method(log_tipo, interfaz, log_all)(safe_method(method)))
        return cls

    return class_decorator
