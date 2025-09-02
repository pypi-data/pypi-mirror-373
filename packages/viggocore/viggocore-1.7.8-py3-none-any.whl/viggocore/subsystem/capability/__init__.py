from viggocore.common import subsystem
from viggocore.subsystem.capability import resource, manager


subsystem = subsystem.Subsystem(resource=resource.Capability,
                                manager=manager.Manager)
