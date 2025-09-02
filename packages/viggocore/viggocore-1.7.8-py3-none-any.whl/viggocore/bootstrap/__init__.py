from viggocore.common.subsystem.apihandler import Api
from typing import Dict, List

from viggocore.common.subsystem import Subsystem
from viggocore.common.input import RouteResource
from viggocore.bootstrap.default import BootstrapDefault
from viggocore.bootstrap.routes import BootstrapRoutes


class Bootstrap(object):

    def __init__(self, api: Api,
                 subsystems: Dict[str, Subsystem],
                 user_resources: List[RouteResource],
                 sysadmin_resources: List[RouteResource],
                 sysadmin_exclusive_resources: List[RouteResource]):
        self.user_resources = user_resources
        self.sysadmin_resources = sysadmin_resources
        self.sysadmin_exclusive_resources = sysadmin_exclusive_resources

        self.routes = BootstrapRoutes(subsystems, api)
        self.default = BootstrapDefault(api)
        self.application_manager = api.applications()

    def execute(self):
        self.routes.execute()

        if not self.application_manager.list():
            self.default.execute(self.user_resources,
                                 self.sysadmin_resources,
                                 self.sysadmin_exclusive_resources)
