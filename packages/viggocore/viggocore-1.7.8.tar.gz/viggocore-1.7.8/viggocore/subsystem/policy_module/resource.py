from sqlalchemy import orm, UniqueConstraint

from viggocore.database import db
from viggocore.common.subsystem import entity
from datetime import datetime


class PolicyModule(entity.Entity, db.Model):

    attributes = ['capability_module_id', 'role_id']
    attributes += entity.Entity.attributes

    capability_module_id = db.Column(
        db.CHAR(32), db.ForeignKey("capability_module.id"),
        nullable=False)
    capability_module = orm.relationship(
        'CapabilityModule',
        backref=orm.backref('policy_module_capability_module'))
    role_id = db.Column(db.CHAR(32), db.ForeignKey("role.id"), nullable=False)
    role = orm.relationship(
        'Role', backref=orm.backref('policy_module_role'))

    __table_args__ = (
        UniqueConstraint(
            'capability_module_id', 'role_id',
            name='pm_capability_module_id_role_id_uk'),)

    def __init__(self, id, capability_module_id, role_id,
                 active=True, created_at=datetime.now(), created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.capability_module_id = capability_module_id
        self.role_id = role_id

    @classmethod
    def individual(cls):
        return 'policy_module'

    @classmethod
    def collection(cls):
        return 'policy_modules'
