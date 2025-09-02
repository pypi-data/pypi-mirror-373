from viggocore.common import subsystem
from viggocore.subsystem.policy_module \
    import manager, resource, controller, router

subsystem = subsystem.Subsystem(resource=resource.PolicyModule,
                                controller=controller.Controller,
                                manager=manager.Manager,
                                router=router.Router)
