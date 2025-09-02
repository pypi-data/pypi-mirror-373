from viggocore.common import subsystem
from viggocore.subsystem.constant_for_calculation \
    import resource, router, controller, manager

subsystem = subsystem.Subsystem(resource=resource.ConstantForCalculation,
                                router=router.Router,
                                controller=controller.Controller,
                                manager=manager.Manager)
