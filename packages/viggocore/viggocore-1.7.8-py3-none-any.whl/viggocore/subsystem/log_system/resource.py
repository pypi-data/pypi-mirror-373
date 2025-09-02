from sqlalchemy import orm

from viggocore.common.subsystem import entity
from viggocore.database import db


class LogSystem(entity.Entity, db.Model):

    attributes = ['domain_id', 'user_id', 'user_name', 'user_password',
                  'justificativa', 'entidade_ids', 'entidade_nome',
                  'json_anterior', 'json_posterior']
    attributes += entity.Entity.attributes

    # ligações
    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey('domain.id'), nullable=False)
    user_id = db.Column(
        db.CHAR(32), db.ForeignKey('user.id'), nullable=False)

    # colunas
    user_name = db.Column(db.String(80), nullable=True)
    user_password = db.Column(db.String(64), nullable=True)
    justificativa = db.Column(db.String(500), nullable=True)
    entidade_ids = db.Column(db.Text, nullable=False)
    entidade_nome = db.Column(db.String(60), nullable=False)
    json_anterior = db.Column(db.Text, nullable=False)
    json_posterior = db.Column(db.Text, nullable=False)

    # backrefs
    user = orm.relationship(
        "User", backref=orm.backref('log_system_user'),
        viewonly=True)

    def __init__(self, id, domain_id, user_id, user_name, entidade_ids,
                 entidade_nome, json_anterior, json_posterior,
                 user_password=None, justificativa=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by, updated_at,
                         updated_by, tag)
        self.domain_id = domain_id
        self.user_id = user_id
        self.user_name = user_name
        self.entidade_ids = entidade_ids
        self.entidade_nome = entidade_nome
        self.json_anterior = json_anterior
        self.json_posterior = json_posterior
        self.user_password = user_password
        self.justificativa = justificativa

    @classmethod
    def individual(self):
        return 'log_system'

    @classmethod
    def collection(cls):
        return 'log_systems'
