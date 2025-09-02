import json
from typing import Any
from sqlalchemy import orm

from viggocore.database import db
from viggocore.common.subsystem import entity
from viggocore.common import exception


class Domain(entity.Entity, db.Model):

    DEFAULT = 'default'

    attributes = ['name', 'display_name', 'parent_id',
                  'application_id', 'logo_id', 'doc', 'description', 'settings']
    attributes += entity.Entity.attributes

    application_id = db.Column(
        db.CHAR(32), db.ForeignKey("application.id"), nullable=False)
    application = orm.relationship('Application', backref=orm.backref(
        'domains'))
    name = db.Column(db.String(60), nullable=False, unique=True)
    display_name = db.Column(db.String(100), nullable=False)
    doc = db.Column(db.String(60), nullable=True)
    description = db.Column(db.String(1000), nullable=True)
    logo_id = db.Column(db.CHAR(32), db.ForeignKey('image.id'), nullable=True)
    parent_id = db.Column(
        db.CHAR(32), db.ForeignKey("domain.id"), nullable=True)
    addresses = orm.relationship(
        'DomainAddress', backref=orm.backref('domain_addresses'),
        cascade='delete,delete-orphan,save-update')
    contacts = orm.relationship(
        'DomainContact', backref=orm.backref('domain_contacts'),
        cascade='delete,delete-orphan,save-update')
    _settings = db.Column('settings', db.Text, nullable=False, default='{}')

    __tablename__ = 'domain'

    def __init__(self, id, application_id, name, display_name=None,
                 doc=None, description=None, logo_id=None, parent_id=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.application_id = application_id
        self.name = name
        if display_name is None:
            self.display_name = name
        else:
            self.display_name = display_name
        self.doc = doc
        self.description = description
        self.logo_id = logo_id
        self.parent_id = parent_id

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

    def get_domain_id(self):
        return self.id

    @property
    def settings(self):
        try:
            settings_str = '{}' if self._settings is None else self._settings
            return json.loads(settings_str)
        except Exception:
            return {}

    def _save_settings(self, settings: dict):
        self._settings = json.dumps(settings, default=str)

    @classmethod
    def embedded(cls):
        return ['addresses', 'contacts']


class DomainAddress(entity.Entity, db.Model):

    attributes = ['logradouro', 'domain_id', 'municipio_id', 'pais_id',
                  'numero', 'complemento', 'bairro', 'ponto_referencia', 'cep']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)
    municipio_id = db.Column(
        db.CHAR(32), db.ForeignKey('municipio.id'), nullable=False)
    municipio = orm.relationship(
        'Municipio', backref=orm.backref('domain_address_municipio'))
    pais_id = db.Column(
        db.CHAR(32), db.ForeignKey('pais.id'), nullable=True)
    pais = orm.relationship(
        'Pais', backref=orm.backref('domain_address_pais'))

    logradouro = db.Column(db.String(255), nullable=False)
    numero = db.Column(db.String(60), nullable=False)
    complemento = db.Column(db.String(60), nullable=True)
    bairro = db.Column(db.String(60), nullable=False)
    ponto_referencia = db.Column(db.String(512), nullable=True)
    cep = db.Column(db.CHAR(8), nullable=False)
    

    def __init__(self, id, domain_id, municipio_id, logradouro, numero,
                 bairro, cep,
                 pais_id=None, complemento=None, ponto_referencia=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.municipio_id = municipio_id
        self.logradouro = logradouro
        self.numero = numero
        self.bairro = bairro
        self.cep = cep
        self.pais_id = pais_id
        self.complemento = complemento
        self.ponto_referencia = ponto_referencia


class DomainContact(entity.Entity, db.Model):

    attributes = ['contact', 'tag']

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey("domain.id"), nullable=False)
    contact = db.Column(db.String(100), nullable=False)

    def __init__(self, id, domain_id, contact,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.contact = contact
