import traceback

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from isapilib.core.utilities import is_test


def safe_method(view_func):
    def wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except APIException as e:
            raise e
        except Exception as e:
            if is_test() or settings.DEBUG: traceback.print_exc()
            return Response({
                'type': str(type(e)),
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return wrapped_view
