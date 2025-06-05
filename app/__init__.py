from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets

db = SQLAlchemy()
app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maraelfit.db'

# Filtro para formatar CPF
@app.template_filter('format_cpf')
def format_cpf(cpf):
    if not cpf:
        return ''
    cpf_str = str(cpf)
    if len(cpf_str) == 11 and cpf_str.isdigit():
        return f'{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}'
    return cpf_str

db.init_app(app)

with app.app_context():
    from app.model.aluno import Aluno
    from app.model.pagamento import Pagamento
    db.create_all()

from app import rotas
