from viggocore.common import subsystem
from viggocore.subsystem.timeline_event \
    import resource, controller, manager


subsystem = subsystem.Subsystem(resource=resource.TimelineEvent,
                                controller=controller.Controller,
                                manager=manager.Manager)
