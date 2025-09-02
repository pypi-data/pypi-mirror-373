from sqlalchemy import orm, UniqueConstraint

from viggocore.database import db
from viggocore.common.subsystem import entity
from datetime import datetime


class CapabilityModule(entity.Entity, db.Model):

    attributes = ['module_id', 'application_id']
    attributes += entity.Entity.attributes

    module_id = db.Column(
        db.CHAR(32), db.ForeignKey("module.id"), nullable=False)
    module = orm.relationship(
        'Module', backref=orm.backref('capability_module_module'))
    application_id = db.Column(
        db.CHAR(32), db.ForeignKey("application.id"), nullable=False)
    application = orm.relationship('Application', backref=orm.backref(
        'capability_module_application'))

    __table_args__ = (
        UniqueConstraint(
            'module_id', 'application_id',
            name='cp_module_id_application_id_uk'),)

    def __init__(self, id, module_id, application_id,
                 active=True, created_at=datetime.now(), created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.module_id = module_id
        self.application_id = application_id

    @classmethod
    def individual(cls):
        return 'capability_module'

    @classmethod
    def collection(cls):
        return 'capability_modules'
