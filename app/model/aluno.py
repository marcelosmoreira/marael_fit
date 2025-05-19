from app import *

class Aluno(db.Model):
    __tablename__ = 'aluno'

    id_aluno = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    data_matricula = db.Column(db.Date, nullable=False)
    data_desligamento = db.Column(db.Date, nullable=True)
    data_vencimento = db.Column(db.Date, nullable=False)