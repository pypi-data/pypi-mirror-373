from isapilib.api.models import BranchAPI
from isapilib.core.exceptions import SepaException


def add_conn(user, branch: BranchAPI):
    name = branch.connection.create_connection()
    if not branch.check_permissions(user):
        raise SepaException(f'You do not have permissions on this connection [{user.pk}, {branch.pk}]', user, branch)
    return name
