from viggocore.common import subsystem
from viggocore.subsystem.token import manager
from viggocore.subsystem.token import resource
from viggocore.subsystem.token import router
from viggocore.subsystem.token import controller

subsystem = subsystem.Subsystem(resource=resource.Token,
                                manager=manager.Manager,
                                router=router.Router,
                                controller=controller.Controller)
