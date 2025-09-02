from viggocore.common import subsystem
from viggocore.subsystem.file import resource
from viggocore.subsystem.file import manager
from viggocore.subsystem.file import controller

subsystem = subsystem.Subsystem(resource=resource.File,
                                manager=manager.Manager,
                                controller=controller.Controller)
