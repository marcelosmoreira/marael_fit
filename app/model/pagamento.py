from app import db
from datetime import date

class Pagamento(db.Model):
    __tablename__ = 'Pagamento'
    __table_args__ = {'sqlite_autoincrement': True}

    id_pagamento = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('Aluno.id_aluno'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)
    data_vencimento = db.Column(db.Date, nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)
    status_pagamento = db.Column(db.String(10), nullable=False, default='Pendente')

    aluno = db.relationship('Aluno', back_populates='pagamentos')

    FORMAS_VALIDAS = ['Não definida', 'Dinheiro', 'Cartão']

    def __init__(self, id_aluno, valor, data_vencimento, data_pagamento=None, forma_pagamento='Não definida'):
        self.id_aluno = id_aluno
        self.valor = valor
        self.data_vencimento = data_vencimento
        self.forma_pagamento = forma_pagamento.capitalize() if forma_pagamento.capitalize() in self.FORMAS_VALIDAS else 'Não definida'
        self.data_pagamento = data_pagamento
        self.ajustar_data_pagamento()
        self.status_pagamento = self.calcular_status_pagamento()

    def ajustar_data_pagamento(self):
        if self.forma_pagamento == 'Não definida':
            self.data_pagamento = None

    def calcular_status_pagamento(self):
        forma = self.forma_pagamento.capitalize()
        hoje = date.today()

        if forma in ['Dinheiro', 'Cartão']:
            return 'Pago'
        elif forma == 'Não definida':
            if self.data_vencimento < hoje:
                return 'Atrasado'
            else:
                return 'Pendente'
        else:
            if self.data_pagamento:
                return 'Pago'
            elif self.data_vencimento < hoje:
                return 'Atrasado'
            else:
                return 'Pendente'

    def atualizar_status(self):
        self.status_pagamento = self.calcular_status_pagamento()
        db.session.commit()

    @staticmethod
    def cadastrar_pagamento(id_aluno, valor, data_vencimento, data_pagamento=None, forma_pagamento='Não definida'):
        try:
            pagamento = Pagamento(
                id_aluno=id_aluno,
                valor=valor,
                data_vencimento=data_vencimento,
                data_pagamento=data_pagamento,
                forma_pagamento=forma_pagamento
            )
            db.session.add(pagamento)
            db.session.commit()
            return pagamento
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao cadastrar pagamento: {e}")

    @staticmethod
    def atualizar_pagamento(id_pagamento, valor, data_vencimento, data_pagamento=None, forma_pagamento='Não definida'):
        try:
            pagamento = db.session.query(Pagamento).get(id_pagamento)
            if pagamento:
                pagamento.valor = valor
                pagamento.data_vencimento = data_vencimento
                pagamento.forma_pagamento = forma_pagamento.capitalize() if forma_pagamento.capitalize() in Pagamento.FORMAS_VALIDAS else 'Não definida'
                pagamento.data_pagamento = data_pagamento
                pagamento.ajustar_data_pagamento()
                pagamento.atualizar_status()
                db.session.commit()
                return pagamento
            else:
                print("Pagamento não encontrado.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar pagamento: {e}")

    @staticmethod
    def deletar_pagamento(id_pagamento):
        try:
            pagamento = db.session.query(Pagamento).get(id_pagamento)
            if pagamento:
                db.session.delete(pagamento)
                db.session.commit()
            else:
                print("Pagamento não encontrado.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar pagamento: {e}")
