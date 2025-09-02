from viggocore.common import subsystem
from viggocore.subsystem.domain_sequence \
    import resource, controller, manager, router, driver


subsystem = subsystem.Subsystem(resource=resource.DomainSequence,
                                controller=controller.Controller,
                                manager=manager.Manager,
                                router=router.Router,
                                driver=driver.Driver)
