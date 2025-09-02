from sqlalchemy import orm, UniqueConstraint

from viggocore.database import db
from viggocore.common.subsystem import entity
from viggocore.common.utils import random_uuid
from viggocore.common import exception


class Module(entity.Entity, db.Model):

    CODE_SEQUENCE = 'module_seq'

    attributes = ['code', 'name', 'description']
    attributes += entity.Entity.attributes

    code = db.Column(db.Numeric(10), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=True)

    functionalities = orm.relationship(
        'ModuleFunctionality',
        backref=orm.backref('module_functionalities'),
        cascade='delete,delete-orphan,save-update')

    def __init__(self, id, code, name, description=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.code = code
        self.name = name
        self.description = description

    def _get_functionality(self, functionality_id):
        functionality = next((r for r in self.functionalities
                              if r.functionality_id == functionality_id), None)
        if not functionality:
            raise exception.BadRequest('ERRO! Functionality not found!')

        return functionality

    def add_functionality(self, functionality_id):
        try:
            self._get_functionality(functionality_id)
        except Exception:
            functionality = ModuleFunctionality(
                random_uuid(), self.id, functionality_id)
            self.functionalities.append(functionality)

    def rm_functionality(self, functionality_id):
        functionality = self._get_functionality(functionality_id)
        self.functionalities.remove(functionality)

    def add_functionalities(self, functionality_ids):
        for functionality_id in functionality_ids:
            self.add_functionality(functionality_id)
        return self

    def rm_functionalities(self, functionality_ids):
        for functionality_id in functionality_ids:
            self.rm_functionality(functionality_id)
        return self

    @classmethod
    def individual(cls):
        return 'module'

    @classmethod
    def collection(cls):
        return 'modules'


class ModuleFunctionality(entity.Entity, db.Model):

    attributes = ['id', 'module_id', 'functionality_id']

    module_id = db.Column(
        db.CHAR(32), db.ForeignKey('module.id'), nullable=False)
    module = orm.relationship(
        'Module',
        backref=orm.backref('module_functionality_module'),
        viewonly=True)
    functionality_id = db.Column(
        db.CHAR(32), db.ForeignKey("functionality.id"), nullable=False)
    functionality = orm.relationship(
        'Functionality',
        backref=orm.backref('module_functionality_functionality'))

    __table_args__ = (UniqueConstraint(
        'module_id', 'functionality_id',
        name=('module_functionality_module_id_functionality_id_uk')),)

    def __init__(self, id, module_id, functionality_id,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.module_id = module_id
        self.functionality_id = functionality_id

    @classmethod
    def individual(cls):
        return ['module_functionality']

    @classmethod
    def collection(cls):
        return ['module_functionalities']
