from enum import Enum

import sqlalchemy
from viggocore.common.subsystem import entity
from viggocore.database import db
from sqlalchemy import UniqueConstraint


class RoleDataViewType(Enum):
    MULTI_DOMAIN = {
        'id': 0,
        'description': 'tem acesso aos dados de mais de um domínio.'}
    DOMAIN = {
        'id': 1,
        'description': 'tem acesso aos dados de apenas um domínio.'}


class Role(entity.Entity, db.Model):

    USER = 'User'
    SYSADMIN = 'Sysadmin'
    ADMIN = 'Admin'
    SUPORTE = 'Suporte'

    attributes = ['name', 'data_view']
    attributes += entity.Entity.attributes

    name = db.Column(db.String(80), nullable=False)
    data_view = db.Column(sqlalchemy.Enum(RoleDataViewType), nullable=False,
                          default=RoleDataViewType.DOMAIN,
                          server_default='DOMAIN')

    __table_args__ = (
        UniqueConstraint('name', name='role_name_uk'),)

    def __init__(self, id, name, data_view,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.name = name
        self.data_view = data_view
