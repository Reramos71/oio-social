from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configurações
app.secret_key = os.environ.get('SECRET_KEY', 'oio_chave_secreta_123')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///oio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

class Perfil(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    foto = db.Column(db.String(200), default='default.jpg')
    data_nascimento = db.Column(db.String(20), default='')
    local_nascimento = db.Column(db.String(100), default='')
    estado = db.Column(db.String(50), default='')
    estado_civil = db.Column(db.String(30), default='')
    interesses = db.Column(db.String(200), default='')
    autobiografia = db.Column(db.String(500), default='')
    status = db.Column(db.String(100), default='')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conteudo = db.Column(db.String(300), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

# Criar banco + pasta + admin
with app.app_context():
    db.create_all()
    os.makedirs('static/foto_perfil', exist_ok=True)

    if not Usuario.query.filter_by(email="admin@oio.com").first():
        admin = Usuario(
            nome="Administrador",
            email="admin@oio.com",
            senha="123456"
        )
        db.session.add(admin)
        db.session.commit()

# --- ROTAS ---
@app.route('/')
def home():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('feed'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            return redirect(url_for('feed'))
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        if Usuario.query.filter_by(email=email).first():
            return "Email já cadastrado"

        novo = Usuario(nome=nome, email=email, senha=senha)
        db.session.add(novo)
        db.session.commit()

        session['usuario_id'] = novo.id
        session['usuario_nome'] = novo.nome

        return redirect(url_for('editar_perfil'))

    return render_template('cadastro.html')

@app.route('/perfil/<int:usuario_id>')
def ver_perfil(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    perfil = Perfil.query.get(usuario_id)

    if not perfil:
        perfil = Perfil(id=usuario_id)
        db.session.add(perfil)
        db.session.commit()

    return render_template('perfil.html', usuario=usuario, perfil=perfil)

@app.route('/editar_perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    perfil = Perfil.query.get(session['usuario_id'])

    if not perfil:
        perfil = Perfil(id=session['usuario_id'])
        db.session.add(perfil)
        db.session.commit()

    if request.method == 'POST':
        perfil.data_nascimento = request.form.get('data_nascimento', '')
        perfil.local_nascimento = request.form.get('local_nascimento', '')
        perfil.estado = request.form.get('estado', '')
        perfil.estado_civil = request.form.get('estado_civil', '')
        perfil.interesses = request.form.get('interesses', '')
        perfil.autobiografia = request.form.get('autobiografia', '')
        perfil.status = request.form.get('status', '')

        db.session.commit()
        return redirect(url_for('ver_perfil', usuario_id=session['usuario_id']))

    return render_template('editar_perfil.html', perfil=perfil)

@app.route('/feed')
def feed():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    posts = Post.query.order_by(Post.data_criacao.desc()).all()
    return render_template('feed.html', posts=posts)

@app.route('/postar', methods=['POST'])
def postar():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    conteudo = request.form['conteudo']

    if not conteudo:
        return redirect(url_for('feed'))

    novo_post = Post(conteudo=conteudo, usuario_id=session['usuario_id'])
    db.session.add(novo_post)
    db.session.commit()

    return redirect(url_for('feed'))

@app.route('/sair')
def sair():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
