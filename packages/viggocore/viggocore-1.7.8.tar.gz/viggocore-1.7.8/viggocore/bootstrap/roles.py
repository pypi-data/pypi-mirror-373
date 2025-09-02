from viggocore.common.subsystem.apihandler import Api
import uuid

from typing import Dict, List

from viggocore.common.subsystem import Subsystem
from viggocore.subsystem.role.resource import Role, RoleDataViewType


class BootstrapRoles(object):

    def __init__(self, api: Api) -> None:
        self.role_manager = api.roles()

    def execute(self):
        roles = self.role_manager.list()
        if not roles:
            default_roles = self._default_roles()
            roles = self.role_manager.create_roles(roles=default_roles)
        return roles

    def _get_role(self, name: str, data_view: RoleDataViewType) -> Role:
        role = Role(id=uuid.uuid4().hex, name=name, data_view=data_view)
        return role

    def _default_roles(self) -> List[Role]:
        user = self._get_role(Role.USER, RoleDataViewType.DOMAIN)
        sysadmin = self._get_role(Role.SYSADMIN, RoleDataViewType.MULTI_DOMAIN)
        admin = self._get_role(Role.ADMIN, RoleDataViewType.DOMAIN)
        suporte = self._get_role(Role.SUPORTE, RoleDataViewType.MULTI_DOMAIN)

        return [user, sysadmin, admin, suporte]
