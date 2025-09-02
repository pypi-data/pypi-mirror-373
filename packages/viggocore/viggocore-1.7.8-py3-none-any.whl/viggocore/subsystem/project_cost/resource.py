from sqlalchemy import orm

from viggocore.database import db
from viggocore.common.subsystem import entity


class ProjectCost(entity.Entity, db.Model):

    attributes = ['name', 'cost']
    attributes += entity.Entity.attributes

    name = db.Column(db.String(30), nullable=False)
    cost = db.Column(db.Numeric(13, 3), nullable=False)

    def __init__(self, id, name, cost,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.name = name
        self.cost = cost

    @classmethod
    def individual(cls):
        return 'project_cost'
