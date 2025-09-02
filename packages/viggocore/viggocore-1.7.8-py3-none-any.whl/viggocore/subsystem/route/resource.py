from viggocore.database import db
from sqlalchemy import UniqueConstraint
from viggocore.common.subsystem import entity
from datetime import datetime


class Route(entity.Entity, db.Model):

    attributes = ['name', 'url', 'method', 'sysadmin', 'bypass', 'projeto']
    attributes += entity.Entity.attributes

    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(80), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    bypass = db.Column(db.Boolean(), nullable=False)
    sysadmin = db.Column(db.Boolean(), nullable=False)
    projeto = db.Column(db.Boolean(), nullable=True)

    __table_args__ = (UniqueConstraint('url', 'method', name='route_uk'),)

    def __init__(self, id, name, url, method, bypass=False, sysadmin=False,
                 projeto=None,
                 active=True, created_at=datetime.now(), created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.name = name
        self.url = url
        self.method = method
        self.bypass = bypass
        self.sysadmin = sysadmin
        self.projeto = projeto
