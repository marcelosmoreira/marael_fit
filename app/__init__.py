import secrets
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

secret_key = secrets.token_hex(16)

with open('secret_key.txt', 'w') as f:
    f.write(secret_key)

app.config['SECRET_KEY'] = secret_key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maraelfit.db'
db = SQLAlchemy(app)

from app import rotas
