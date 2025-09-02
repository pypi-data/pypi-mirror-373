from viggocore.common import subsystem
from viggocore.subsystem.capability_functionality \
    import manager, resource, controller, router

subsystem = subsystem.Subsystem(resource=resource.CapabilityFunctionality,
                                controller=controller.Controller,
                                manager=manager.Manager,
                                router=router.Router)
