from app import db
from datetime import date, timedelta

class Pagamento(db.Model):
    __tablename__ = 'Pagamento'
    __table_args__ = {'sqlite_autoincrement': True}

    id_pagamento = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('Aluno.id_aluno'), nullable=False)
    data = db.Column(db.Date, nullable=False, default=date.today)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)

    aluno = db.relationship('Aluno', backref=db.backref('pagamentos', lazy=True))

    def __init__(self, id_aluno, valor, tipo):
        self.id_aluno = id_aluno
        self.data = date.today()
        self.valor = valor
        self.tipo = tipo

    @staticmethod
    def registrar_pagamento(id_aluno, valor, tipo):
        try:
            if tipo not in ["dinheiro", "cartão"]:
                print("Tipo de pagamento inválido. Use 'dinheiro' ou 'cartão'.")
                return None

            novo_pagamento = Pagamento(id_aluno, valor, tipo)
            db.session.add(novo_pagamento)

            from model.aluno import Aluno
            aluno = db.session.query(Aluno).filter(Aluno.id_aluno == id_aluno).first()

            if aluno:
                aluno.data_matricula = date.today() if not aluno.data_matricula else aluno.data_matricula
                aluno.data_desligamento = None
                aluno.data_vencimento = date.today() + timedelta(days=30)

            db.session.commit()
            return novo_pagamento
        except Exception as erro:
            db.session.rollback()
            print("Erro ao registrar pagamento:", erro)

    @staticmethod
    def consultar_pagamentos(id_aluno):
        try:
            return db.session.query(Pagamento).filter(Pagamento.id_aluno == id_aluno).all()
        except Exception as erro:
            print("Erro ao consultar pagamentos:", erro)
            return []

    @staticmethod
    def atualizar_pagamento(id_pagamento, valor, tipo):
        try:
            if tipo not in ["dinheiro", "cartão"]:
                print("Tipo de pagamento inválido.")
                return False

            db.session.query(Pagamento).filter(Pagamento.id_pagamento == id_pagamento).update({"valor": valor,"tipo": tipo})
            db.session.commit()
            return True
        except Exception as erro:
            db.session.rollback()
            print("Erro ao atualizar pagamento:", erro)
            return False

    @staticmethod
    def deletar_pagamento(id_pagamento):
        try:
            pagamento = db.session.query(Pagamento).filter(Pagamento.id_pagamento == id_pagamento).first()
            if pagamento:
                db.session.delete(pagamento)
                db.session.commit()
                return True
            else:
                print("Pagamento não encontrado.")
                return False
        except Exception as erro:
            db.session.rollback()
            print("Erro ao deletar pagamento:", erro)
            return False
