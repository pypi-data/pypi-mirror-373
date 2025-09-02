from viggocore.common import subsystem
from viggocore.subsystem.alembic_version_history import resource, router

subsystem = subsystem.Subsystem(resource=resource.AlembicVersionHistory,
                                router=router.Router)
