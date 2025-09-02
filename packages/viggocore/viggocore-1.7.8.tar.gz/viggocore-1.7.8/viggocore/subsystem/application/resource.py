import json
from typing import Any

from viggocore.common import exception
from viggocore.common.subsystem import entity
from viggocore.database import db
from sqlalchemy import UniqueConstraint


class Application(entity.Entity, db.Model):

    DEFAULT = "default"

    attributes = ['name', 'description', 'settings', 'customized']
    attributes += entity.Entity.attributes

    pagination_column = 'name'

    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    _settings = db.Column('settings', db.Text, nullable=False, default='{}',
                          server_default='{}')
    customized = db.Column(db.Boolean(), nullable=False, default=False,
                           server_default='false')

    __table_args__ = (UniqueConstraint('name', name='application_name_uk'),)

    def __init__(self, id, name, description, customized=False,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.name = name
        self.description = description
        self.customized = customized

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
