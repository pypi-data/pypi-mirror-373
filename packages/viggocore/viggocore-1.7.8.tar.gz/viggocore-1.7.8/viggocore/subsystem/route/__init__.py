from viggocore.common import subsystem
from viggocore.subsystem.route import resource, manager


subsystem = subsystem.Subsystem(resource=resource.Route,
                                manager=manager.Manager)
