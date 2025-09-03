import threading

from rest_framework.permissions import BasePermission

_thread_local = threading.local()


class IsapilibPermission(BasePermission):
    def has_permission(self, request, view):
        self.set_current_request(request)
        return True

    @staticmethod
    def get_current_request():
        request = getattr(_thread_local, 'request', None)
        if request is None:
            raise Exception(
                'Request is not available in thread-local context. '
                'Make sure IsapilibPermission is set either in DEFAULT_PERMISSION_CLASSES '
                'or included in the view\'s permission_classes.'
            )
        return request

    @staticmethod
    def set_current_request(request):
        _thread_local.request = request
