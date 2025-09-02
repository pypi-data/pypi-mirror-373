from viggocore.common import subsystem, controller
from viggocore.subsystem.project_cost \
    import resource, manager

subsystem = subsystem.Subsystem(resource=resource.ProjectCost,
                                manager=manager.Manager,
                                controller=controller.CommonController)
