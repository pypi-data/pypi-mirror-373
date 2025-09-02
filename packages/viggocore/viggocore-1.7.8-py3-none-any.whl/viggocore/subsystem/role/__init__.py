from viggocore.common import subsystem
from viggocore.subsystem.role \
    import resource, router, controller, manager

subsystem = subsystem.Subsystem(resource=resource.Role,
                                router=router.Router,
                                controller=controller.Controller,
                                manager=manager.Manager)
