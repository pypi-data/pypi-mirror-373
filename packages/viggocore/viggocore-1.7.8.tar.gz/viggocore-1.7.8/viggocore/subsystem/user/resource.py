from enum import Enum
import uuid
import json
from typing import Any
from sqlalchemy import orm
from viggocore.database import db
from sqlalchemy import UniqueConstraint
from viggocore.common import exception
from viggocore.common.subsystem import entity


class CREATE_TYPE(Enum):
    # o backend gera automaticamente
    GENERATE_PASSWORD = 'GENERATE_PASSWORD'
    # o front passa a senha
    INPUT_PASSWORD = 'INPUT_PASSWORD'
    # senha default que o backend define que será o hash 123456
    DEFAULT_PASSWORD = 'DEFAULT_PASSWORD'


class User(entity.Entity, db.Model):

    SYSADMIN_USERNAME = 'sysadmin'

    attributes = ['domain_id', 'name', 'email', 'nickname', 'photo_id',
                  'settings']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)
    domain = orm.relationship('Domain', backref=orm.backref('users'))
    name = db.Column(db.String(80), nullable=False)
    nickname = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(
        db.String(64), nullable=False, default=uuid.uuid4().hex)
    photo_id = db.Column(db.CHAR(32), db.ForeignKey('image.id'), nullable=True)
    _settings = db.Column('settings', db.Text, nullable=False, default='{}')

    tokens = orm.relationship('Token', backref=orm.backref('user_tokens'))

    __table_args__ = (
        UniqueConstraint('name', 'domain_id', name='user_name_domain_id_uk'),
        UniqueConstraint(
            'email', 'domain_id', name='user_email_domain_id_uk'),)

    def __init__(self, id, domain_id, name, email,
                 nickname=None, photo_id=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.name = name
        self.email = email
        # self.password = password
        self.nickname = nickname
        self.photo_id = photo_id

    def _has_setting(self, key: str) -> bool:
        return self.settings.get(key) is not None

    def remove_setting(self, key: str):
        if not self._has_setting(key):
            raise exception.BadRequest(f"Erro! Setting {key} not exists")

        settings = self.settings
        value = settings.pop(key)
        self._save_settings(settings)

        return value

    def update_setting(self, key: str, value: Any):
        settings = self.settings
        settings[key] = value
        self._save_settings(settings)
        return value

    @property
    def settings(self):
        try:
            settings_str = '{}' if self._settings is None else self._settings
            return json.loads(settings_str)
        except Exception:
            return {}

    def _save_settings(self, settings: dict):
        self._settings = json.dumps(settings, default=str)
