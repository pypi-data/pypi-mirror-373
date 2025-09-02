from datetime import datetime
from viggocore.database import db
from viggocore.common.subsystem import entity


class Token(entity.Entity, db.Model):

    attributes = ['user_id', 'natureza']
    attributes += entity.Entity.attributes

    user_id = db.Column(db.CHAR(32), db.ForeignKey("user.id"), nullable=False)
    natureza = db.Column(db.String(20), nullable=True)

    def __init__(self, id, user_id, natureza=None,
                 active=True, created_at=datetime.now(),
                 created_by=user_id, updated_at=None,
                 updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.user_id = user_id
        self.natureza = natureza
