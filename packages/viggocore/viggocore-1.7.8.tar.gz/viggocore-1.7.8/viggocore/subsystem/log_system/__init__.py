
from viggocore.common import subsystem

from viggocore.subsystem.log_system import \
    manager, resource, router


subsystem = subsystem.Subsystem(resource=resource.LogSystem,
                                manager=manager.Manager,
                                router=router.Router)
