from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets

db = SQLAlchemy()
app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maraelfit.db'

db.init_app(app)

with app.app_context():
    from app.model.aluno import Aluno
    from app.model.pagamento import Pagamento
    db.create_all()

from app import rotas
