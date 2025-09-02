from sqlalchemy import orm, UniqueConstraint

from viggocore.database import db
from viggocore.common.subsystem import entity
from viggocore.common.utils import random_uuid
from viggocore.common import exception


class Functionality(entity.Entity, db.Model):

    CODE_SEQUENCE = 'functionality_seq'

    attributes = ['code', 'name', 'description']
    attributes += entity.Entity.attributes

    code = db.Column(db.Numeric(10), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(1000), nullable=True)

    routes = orm.relationship(
        'FunctionalityRoute',
        backref=orm.backref('functionality_routes'),
        cascade='delete,delete-orphan,save-update')

    def __init__(self, id, code, name, description=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.code = code
        self.name = name
        self.description = description

    def _get_route(self, route_id):
        route = next((r for r in self.routes
                      if r.route_id == route_id), None)
        if not route:
            raise exception.BadRequest('ERRO! Route not found!')

        return route

    def add_route(self, route_id):
        try:
            route = self._get_route(route_id)
        except Exception:
            route = FunctionalityRoute(random_uuid(), self.id, route_id)
            self.routes.append(route)

    def rm_route(self, route_id):
        route = self._get_route(route_id)
        self.routes.remove(route)

    def add_routes(self, route_ids):
        for route_id in route_ids:
            self.add_route(route_id)
        return self

    def rm_routes(self, route_ids):
        for route_id in route_ids:
            self.rm_route(route_id)
        return self

    @classmethod
    def individual(cls):
        return 'functionality'

    @classmethod
    def collection(cls):
        return 'functionalities'


class FunctionalityRoute(entity.Entity, db.Model):

    attributes = ['id', 'functionality_id', 'route_id']

    functionality_id = db.Column(
        db.CHAR(32), db.ForeignKey('functionality.id'), nullable=False)
    functionality = orm.relationship(
        'Functionality',
        backref=orm.backref('functionality_route_functionality'),
        viewonly=True)
    route_id = db.Column(
        db.CHAR(32), db.ForeignKey("route.id"), nullable=False)
    route = orm.relationship(
        'Route',
        backref=orm.backref('functionality_route_route'))

    __table_args__ = (UniqueConstraint(
        'functionality_id', 'route_id',
        name=('functionality_route_functionality_id_route_id_uk')),)

    def __init__(self, id, functionality_id, route_id,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.functionality_id = functionality_id
        self.route_id = route_id

    @classmethod
    def individual(cls):
        return ['functionality_route']

    @classmethod
    def collection(cls):
        return ['functionality_routes']
