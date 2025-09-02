from viggocore.common import subsystem
from viggocore.subsystem.image import resource, manager, controller, router

subsystem = subsystem.Subsystem(resource=resource.Image,
                                manager=manager.Manager,
                                controller=controller.Controller,
                                router=router.Router)
