from viggocore.common import subsystem
from viggocore.subsystem.module \
    import manager, resource, controller, router

subsystem = subsystem.Subsystem(resource=resource.Module,
                                controller=controller.Controller,
                                manager=manager.Manager,
                                router=router.Router)
