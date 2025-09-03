from functools import lru_cache

from rest_framework import settings

from isapilib.api.models import BranchAPI
from isapilib.auth.permissions import IsapilibPermission
from isapilib.core.utilities import is_test
from isapilib.external.connection import add_conn


class BaseRouter:
    default_database = (
        'ConnectionAPI'.lower(),
        'BranchAPI'.lower(),
        'UserAPI'.lower(),
        'PermissionAPI'.lower(),
        'ApiLogs'.lower(),
        'idtoken',
        'accesstoken',
        'refreshtoken',
        'application',
    )

    def get_branch(self, user, request) -> BranchAPI:
        if request.user.branch is None:
            raise Exception(f"User don't have a default branch ({request.user})")
        return request.user.branch

    def external_db(self):
        request = IsapilibPermission.get_current_request()
        branch = self.get_branch(request.user, request)
        return add_conn(request.user, branch)

    def _get_model_name(self, model):
        try:
            return model._meta.model_name
        except Exception as e:
            return 'execution'

    def db_for_read(self, model, **hints):
        if self._get_model_name(model) in self.default_database: return 'default'
        return self.external_db()

    def db_for_write(self, model, **hints):
        if self._get_model_name(model) in self.default_database: return 'default'
        return self.external_db()

    def allow_relation(self, *args, **kwargs):
        return True


@lru_cache
def get_branch(dealer_id: str) -> BranchAPI:
    branch = BranchAPI.objects.filter(gwmbac=dealer_id, gwmbac__isnull=False).first()
    if branch is None: raise BranchAPI.DoesNotExist('El DealerID no existe')
    return branch


class DealerIDRouter(BaseRouter):
    def get_branch(self, user, request) -> BranchAPI:
        if is_test():
            dealer_id = getattr(settings, 'dealerID')
        else:
            dealer_id = request.headers.get('dealerID')
        return get_branch(dealer_id)
