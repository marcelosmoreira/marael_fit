from app import db
from datetime import date, timedelta

class Pagamento(db.Model):
    __tablename__ = 'Pagamento'
    __table_args__ = {'sqlite_autoincrement': True}

    id_pagamento = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('Aluno.id_aluno'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)
    data_vencimento = db.Column(db.Date, nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)
    status_pagamento = db.Column(db.String(10), nullable=False, default='pendente')

    aluno = db.relationship('Aluno', back_populates='pagamentos')

    FORMAS_VALIDAS = ['Dinheiro', 'Cartão']

    def __init__(self, id_aluno, valor, data_vencimento, data_pagamento=None, forma_pagamento='Dinheiro'):
        self.id_aluno = id_aluno
        self.valor = valor
        self.data_vencimento = data_vencimento
        self.data_pagamento = data_pagamento
        if forma_pagamento.capitalize() in self.FORMAS_VALIDAS:
            self.forma_pagamento = forma_pagamento.capitalize()
        else:
            self.forma_pagamento = 'Dinheiro'
        self.status_pagamento = self.calcular_status_pagamento()

    def calcular_status_pagamento(self):
        hoje = date.today()
        if self.data_pagamento:
            return 'pago'
        else:
            dias_atraso = (hoje - self.data_vencimento).days
            if dias_atraso > 30:
                return 'atrasado'
            else:
                return 'pendente'

    def atualizar_status(self):
        self.status_pagamento = self.calcular_status_pagamento()
        db.session.commit()

    @staticmethod
    def cadastrar_pagamento(id_aluno, valor, data_vencimento, data_pagamento=None, forma_pagamento='Dinheiro'):
        try:
            forma_pagamento = forma_pagamento.capitalize()
            if forma_pagamento not in Pagamento.FORMAS_VALIDAS:
                forma_pagamento = 'Dinheiro'

            novo_pagamento = Pagamento(id_aluno, valor, data_vencimento, data_pagamento, forma_pagamento)
            db.session.add(novo_pagamento)
            db.session.commit()
            return novo_pagamento
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao cadastrar pagamento: {e}")

    @staticmethod
    def atualizar_pagamento(id_pagamento, valor, data_vencimento, data_pagamento, forma_pagamento):
        try:
            pagamento = db.session.query(Pagamento).filter(Pagamento.id_pagamento == id_pagamento).first()
            if pagamento:
                pagamento.valor = valor
                pagamento.data_vencimento = data_vencimento
                pagamento.data_pagamento = data_pagamento
                forma_pagamento = forma_pagamento.capitalize()
                if forma_pagamento not in Pagamento.FORMAS_VALIDAS:
                    forma_pagamento = 'Dinheiro'
                pagamento.forma_pagamento = forma_pagamento

                pagamento.atualizar_status()

                if pagamento.status_pagamento == 'pago':
                    existe_proximo = db.session.query(Pagamento).filter(
                        Pagamento.id_aluno == pagamento.id_aluno,
                        Pagamento.data_vencimento > pagamento.data_vencimento
                    ).first()

                    if not existe_proximo:
                        proximo_vencimento = pagamento.data_vencimento + timedelta(days=30)

                        novo_pagamento = Pagamento(
                            id_aluno=pagamento.id_aluno,
                            valor=pagamento.valor,
                            data_vencimento=proximo_vencimento,
                            forma_pagamento=pagamento.forma_pagamento
                        )
                        db.session.add(novo_pagamento)
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
            pagamento = db.session.query(Pagamento).filter(Pagamento.id_pagamento == id_pagamento).first()
            if pagamento:
                db.session.delete(pagamento)
                db.session.commit()
            else:
                print("Pagamento não encontrado.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar pagamento: {e}")
