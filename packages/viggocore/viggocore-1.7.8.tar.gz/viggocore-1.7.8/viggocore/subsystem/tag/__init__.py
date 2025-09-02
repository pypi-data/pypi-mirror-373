from viggocore.common import subsystem
from viggocore.subsystem.tag import resource, router, manager, controller


subsystem = subsystem.Subsystem(resource=resource.Tag,
                                router=router.Router,
                                manager=manager.Manager,
                                controller=controller.Controller)
