from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', 'oio_chave_secreta_123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///oio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

class Perfil(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    foto = db.Column(db.String(200), default='default.jpg')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.String(300), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# 🔥 AQUI É O LUGAR CERTO
with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(email="admin@oio.com").first():
        admin = Usuario(nome="Admin", email="admin@oio.com", senha="admin123")
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
