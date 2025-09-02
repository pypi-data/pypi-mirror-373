import sqlalchemy

from enum import Enum
from viggocore.database import db
from viggocore.common.subsystem import entity
from sqlalchemy import orm


class FILE_SYNC_STATUS(Enum):
    PENDING = 1
    SUCCESS = 2
    ERROR = 3


class FILE_SYNC_MESSAGE_TYPE(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3


class FileSync(entity.Entity, db.Model):
    attributes = ['domain_id', 'file_id', 'status', 'entity', 'entity_id']
    attributes += entity.Entity.attributes

    domain_id = db.Column(
        db.CHAR(32), db.ForeignKey("domain.id"), nullable=False)
    file_id = db.Column(
        db.CHAR(32), db.ForeignKey("file_infosys.id"), nullable=False)
    status = db.Column(sqlalchemy.Enum(FILE_SYNC_STATUS), nullable=False)
    entity = db.Column(db.String(80), nullable=False)
    entity_id = db.Column(db.String(32), nullable=True)

    messages = orm.relationship('FileSyncMessage',
                                backref=orm.backref('file_sync_message'),
                                cascade='delete,delete-orphan,save-update')

    def __init__(self, id, domain_id, file_id, entity, status, entity_id=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.domain_id = domain_id
        self.file_id = file_id
        self.status = status
        self.entity_id = entity_id

    @classmethod
    def embedded(cls):
        return ['messages']


class FileSyncMessage(entity.Entity, db.Model):
    attributes = ['domain_id', 'file_id']
    attributes += entity.Entity.attributes

    file_sync_id = db.Column(
        db.CHAR(32), db.ForeignKey('file_sync.id'), nullable=False)
    type_message = db.Column(sqlalchemy.Enum(FILE_SYNC_MESSAGE_TYPE), nullable=False)
    body = db.Column(db.String(250), nullable=False)

    def __init__(self, id, file_sync_id, type_message, body,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.file_sync_id = file_sync_id
        self.type_message = type_message
        self.body = body
