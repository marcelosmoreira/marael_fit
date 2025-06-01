from app import db
from datetime import date, timedelta

class Aluno(db.Model):
    __tablename__ = 'Aluno'
    __table_args__ = {'sqlite_autoincrement': True}

    id_aluno = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_matricula = db.Column(db.Date, nullable=False, default=date.today)
    data_vencimento = db.Column(db.Date, nullable=False)
    data_desligamento = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(10), nullable=False, default="Ativo")

    pagamentos = db.relationship('Pagamento', back_populates='aluno', lazy=True)

    def __init__(self, nome, cpf, endereco, cidade, estado, telefone, data_matricula=None, data_vencimento=None, data_desligamento=None, status=None):
        self.nome = nome
        self.cpf = cpf
        self.endereco = endereco
        self.cidade = cidade
        self.estado = estado.upper()
        self.telefone = telefone
        self.data_matricula = data_matricula or date.today()
        self.data_vencimento = data_vencimento or (self.data_matricula + timedelta(days=30))
        self.data_desligamento = data_desligamento
        self.status = status or ("Ativo" if data_desligamento is None else "Inativo")

@staticmethod
def cadastrar_aluno(nome, cpf, endereco, cidade, estado, telefone, data_matricula=None):
    try:
        existente = Aluno.buscar_por_cpf(cpf)
        if existente:
            print("Erro: CPF já cadastrado.")
            return None

        novo_aluno = Aluno(nome, cpf, endereco, cidade, estado, telefone, data_matricula)
        db.session.add(novo_aluno)
        db.session.commit()

        data_vencimento = novo_aluno.data_matricula + timedelta(days=30)
        VALOR_PADRAO = 100.00
        from app.model import Pagamento

        pagamento = Pagamento.cadastrar_pagamento(
            id_aluno=novo_aluno.id_aluno,
            valor=VALOR_PADRAO,
            data_vencimento=data_vencimento,
        )

        return novo_aluno

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao cadastrar aluno: {e}")

    @staticmethod
    def atualizar_status_aluno(id_aluno, status_ativo: bool):
        try:
            aluno = db.session.query(Aluno).filter(Aluno.id_aluno == id_aluno).first()
            if aluno:
                if status_ativo:
                    aluno.data_desligamento = None
                    aluno.status = "Ativo"
                else:
                    aluno.data_desligamento = date.today()
                    aluno.status = "Inativo"
                db.session.commit()
                return aluno
            else:
                print("Aluno não encontrado.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar status do aluno: {e}")

    @staticmethod
    def buscar_por_id(id_aluno):
        return db.session.query(Aluno).filter(Aluno.id_aluno == id_aluno).first()

    @staticmethod
    def buscar_por_cpf(cpf):
        return db.session.query(Aluno).filter(Aluno.cpf == cpf).first()

    @staticmethod
    def atualizar_aluno(id_aluno, nome, cpf, endereco, cidade, estado, telefone, data_matricula, data_vencimento, data_desligamento, status=None):
        try:
            aluno = db.session.query(Aluno).filter(Aluno.id_aluno == id_aluno).first()
            if aluno:
                aluno.nome = nome
                aluno.cpf = cpf
                aluno.endereco = endereco
                aluno.cidade = cidade
                aluno.estado = estado.upper()
                aluno.telefone = telefone
                aluno.data_matricula = data_matricula
                aluno.data_vencimento = data_vencimento
                aluno.data_desligamento = data_desligamento
                aluno.status = status or ("Ativo" if data_desligamento is None else "Inativo")
                db.session.commit()
                return aluno
            else:
                print("Aluno não encontrado.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar aluno: {e}")

    @staticmethod
    def deletar_aluno(id_aluno):
        try:
            aluno = db.session.query(Aluno).filter(Aluno.id_aluno == id_aluno).first()
            if aluno:
                db.session.delete(aluno)
                db.session.commit()
            else:
                print("Aluno não encontrado.")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar aluno: {e}")
