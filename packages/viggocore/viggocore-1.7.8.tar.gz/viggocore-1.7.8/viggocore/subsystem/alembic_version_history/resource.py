from viggocore.database import db
from viggocore.common.subsystem import entity


class AlembicVersionHistory(entity.Entity, db.Model):

    attributes = ['titulo', 'anterior_id', 'atual_id',
                  'data_criacao', 'data_execucao', 'tipo']
    attributes += entity.Entity.attributes

    ordem = db.Column(
        db.Integer, nullable=False, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(200), nullable=False)
    anterior_id = db.Column(db.String(50), nullable=True)
    atual_id = db.Column(db.String(50), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False)
    data_execucao = db.Column(db.DateTime, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)

    __tablename__ = 'alembic_version_history'

    def __init__(self, id, titulo, atual_id, data_criacao,
                 data_execucao, tipo, anterior_id=None,
                 active=True, created_at=None, created_by=None,
                 updated_at=None, updated_by=None, tag=None):
        super().__init__(id, active, created_at, created_by,
                         updated_at, updated_by, tag)
        self.titulo = titulo
        self.anterior_id = anterior_id
        self.atual_id = atual_id
        self.data_criacao = data_criacao
        self.data_execucao = data_execucao
        self.tipo = tipo

    @classmethod
    def individual(self):
        return 'alembic_version_history'
