from app import db
from datetime import date, timedelta


class Aluno(db.Model):
    __tablename__ = 'Aluno'
    __table_args__ = {'sqlite_autoincrement': True}
    id_aluno = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    data_matricula = db.Column(db.Date, nullable=True)
    data_desligamento = db.Column(db.Date, nullable=True)
    data_vencimento = db.Column(db.Date, nullable=True)

    def __init__(self, nome, endereco, cidade, estado, telefone, data_matricula=None, data_desligamento=None, data_vencimento=None):
        self.nome = nome
        self.endereco = endereco
        self.cidade = cidade
        self.estado = estado
        self.telefone = telefone
        self.data_matricula = data_matricula
        self.data_desligamento = data_desligamento
        self.data_vencimento = data_vencimento

    @staticmethod
    def cadastrar_aluno(self, nome, endereco, cidade, estado, telefone, data_matricula=None, data_desligamento=None, data_vencimento=None):
        try:
            novo_aluno = Aluno(nome, endereco, cidade, estado, telefone,
                               data_matricula, data_desligamento, data_vencimento)
            db.session.add(novo_aluno)
            db.session.commit()
            return novo_aluno
        except Exception as erro:
            db.session.rollback()
            print("Erro ao cadastrar aluno", erro)

    @staticmethod
    def atualizar_aluno(id_aluno, nome, endereco, cidade, estado, telefone, data_matricula, data_desligamento, data_vencimento):
        try:
            db.session.query(Aluno).filter(Aluno.id_aluno == id_aluno).update({"nome": nome, "endereco": endereco, "cidade": cidade, "estado": estado,
                                                                               "telefone": telefone, "data_matricula": data_matricula, "data_desligamento": data_desligamento, "data_vencimento": data_vencimento})
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Erro ao atualizar o produto", e)

    @staticmethod
    def deletar_aluno(id_aluno):
        try:
            aluno = db.session.query(Aluno).filter(
                Aluno.id_aluno == id_aluno).first()
            if aluno:
                db.session.delete(aluno)
                db.session.commit()
            else:
                print("Aluno não encontrado.")
        except Exception as erro:
            db.session.rollback()
            print("Erro ao deletar aluno:", erro)

    def matricular(self):
        self.data_matricula = date.today()
        self.data_vencimento = self.data_matricula + timedelta(days=30)
        self.data_desligamento = None
        db.session.commit()

    def esta_ativo(self):
        if self.data_matricula and not self.data_desligamento:
            return True
        return False

    def verificar_vencimento(self):
        hoje = date.today()
        if self.esta_ativo() and self.data_vencimento and hoje > self.data_vencimento:
            self.data_desligamento = hoje
            db.session.commit()
