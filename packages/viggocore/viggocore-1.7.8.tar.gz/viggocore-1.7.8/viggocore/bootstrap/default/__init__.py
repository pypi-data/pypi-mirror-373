from typing import Dict, List

from viggocore.common.subsystem import Subsystem
from viggocore.common.subsystem.apihandler import Api
from viggocore.common.input import RouteResource
from viggocore.subsystem.role.resource import Role
from viggocore.bootstrap.roles import BootstrapRoles
from viggocore.bootstrap.default.application import BootstrapApplication
from viggocore.bootstrap.default.domain import BootstrapDomain
from viggocore.bootstrap.default.user import BootstrapUser
from viggocore.bootstrap.default.policies import BootstrapPolicies


class BootstrapDefault(object):

    def __init__(self, api: Api) -> None:
        self.bootstrap_roles = BootstrapRoles(api)
        self.bootstrap_application = BootstrapApplication(api)
        self.bootstrap_domain = BootstrapDomain(api)
        self.bootstrap_user = BootstrapUser(api)
        self.bootstrap_policies = BootstrapPolicies(api)

    def execute(self, user_resources: List[RouteResource],
                sysadmin_resources: List[RouteResource],
                sysadmin_exclusive_resources: List[RouteResource]):
        roles = self.bootstrap_roles.execute()
        role_sysadmin = self._get_role_sysadmin(roles)

        application = self.bootstrap_application.execute()
        domain = self.bootstrap_domain.execute(application.id)
        self.bootstrap_user.execute(domain.id, role_sysadmin.id)
        self.bootstrap_policies.execute(application.id,
                                        role_sysadmin.id,
                                        user_resources,
                                        sysadmin_resources,
                                        sysadmin_exclusive_resources)

    def _get_role_sysadmin(self, roles: List[Role]) -> Role:
        role = next((role for role in roles if role.name == Role.SYSADMIN),
                    None)
        if not role:
            raise Exception()
        return role
