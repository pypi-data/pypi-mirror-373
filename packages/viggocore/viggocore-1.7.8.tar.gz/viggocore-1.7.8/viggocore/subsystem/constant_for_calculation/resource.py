from sqlalchemy import orm, UniqueConstraint

from viggocore.database import db
from viggocore.common.subsystem import entity


class ConstantForCalculation(entity.Entity, db.Model):

    attributes = ['application_id', 'table_name', 'p_processos',
                  'p_acessos_db']
    attributes += entity.Entity.attributes

    application_id = db.Column(
        db.CHAR(32), db.ForeignKey("application.id"), nullable=False)
    application = orm.relationship('Application', backref=orm.backref(
        'constants_for_calculation_application'))
    table_name = db.Column(db.String(60), nullable=False)
    p_processos = db.Column(db.Numeric(5), nullable=False)
    p_acessos_db = db.Column(db.Numeric(5), nullable=False)

    __table_args__ = (UniqueConstraint(
        'application_id', 'table_name',
        name='constant_for_calculation_application_id_table_name_uk'),)

    def __init__(self, id, application_id, table_name, p_processos=1,
                 p_acessos_db=1,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.application_id = application_id
        self.table_name = table_name
        self.p_processos = p_processos
        self.p_acessos_db = p_acessos_db

    @classmethod
    def individual(cls):
        return 'constant_for_calculation'
