from viggocore.common import subsystem
from viggocore.subsystem.user import resource

from viggocore.subsystem.user import controller
from viggocore.subsystem.user import manager
from viggocore.subsystem.user import router


subsystem = subsystem.Subsystem(resource=resource.User,
                                router=router.Router,
                                controller=controller.Controller,
                                manager=manager.Manager)
