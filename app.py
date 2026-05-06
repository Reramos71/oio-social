from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'oio_social_chave_2025'

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Faça login primeiro')
            return redirect('/')
        return f(*args, **kwargs)
    return decorated

def init_db():
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT, apelido TEXT, cidade TEXT, email TEXT UNIQUE, 
        senha TEXT, foto_perfil TEXT, is_admin INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, user_nome TEXT, texto TEXT, 
        curtidas INTEGER DEFAULT 0, tempo TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS recados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        para_user_id INTEGER, de_user_nome TEXT, mensagem TEXT, 
        cutucada INTEGER DEFAULT 0, tempo TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute("SELECT * FROM usuarios WHERE email = 'admin@oio.com'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (nome, apelido, email, senha, is_admin) VALUES (?,?,?,?,?)",
                  ('Administrador', 'admin', 'admin@oio.com', generate_password_hash('admin123'), 1))
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Ôio Social</title>
    <style>
        body{font-family:Arial;background:linear-gradient(135deg,#009c3b,#ffdf00);margin:0;padding:20px}
        .box{background:white;max-width:400px;margin:50px auto;padding:40px;border-radius:20px;text-align:center}
        input,button{width:100%;padding:12px;margin:10px 0;border-radius:8px}
        button{background:#009c3b;color:white;border:none;cursor:pointer;font-weight:bold}
        h1{color:#009c3b}
        a{color:#009c3b}
        .flag{font-size:50px}
    </style>
    </head>
    <body>
    <div class="box">
        <div class="flag">🇧🇷</div>
        <h1>Ôio Social</h1>
        <p>A rede social brasileira</p>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Email ou apelido" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Entrar</button>
        </form>
        <p>Não tem conta? <a href="/cadastro">Criar Conta</a></p>
    </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    senha = request.form['senha']
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT id, nome, senha, is_admin FROM usuarios WHERE email = ? OR apelido = ?", (username, username))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[2], senha):
        session['user_id'] = user[0]
        session['user_nome'] = user[1]
        session['is_admin'] = user[3]
        return redirect('/feed')
    flash('Usuário ou senha incorretos')
    return redirect('/')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        apelido = request.form['apelido']
        cidade = request.form['cidade']
        email = request.form['email']
        senha_hash = generate_password_hash(request.form['senha'])
        conn = sqlite3.connect('oio.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (nome, apelido, cidade, email, senha) VALUES (?,?,?,?,?)",
                      (nome, apelido, cidade, email, senha_hash))
            conn.commit()
            flash('Conta criada com sucesso! Faça login.')
            return redirect('/')
        except:
            flash('Email já cadastrado!')
        finally:
            conn.close()
    return '''
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Cadastro - Ôio Social</title>
    <style>
        body{font-family:Arial;background:linear-gradient(135deg,#009c3b,#ffdf00);margin:0;padding:20px}
        .box{background:white;max-width:500px;margin:50px auto;padding:40px;border-radius:20px}
        input,button{width:100%;padding:12px;margin:10px 0;border-radius:8px}
        button{background:#009c3b;color:white;border:none;cursor:pointer;font-weight:bold}
        h2{color:#009c3b;text-align:center}
        .flag{font-size:40px;text-align:center}
        a{color:#009c3b}
    </style>
    </head>
    <body>
    <div class="box">
        <div class="flag">🇧🇷</div>
        <h2>Criar Conta</h2>
        <form method="POST">
            <input type="text" name="nome" placeholder="Nome completo" required>
            <input type="text" name="apelido" placeholder="Apelido" required>
            <input type="text" name="cidade" placeholder="Sua cidade" required>
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Cadastrar</button>
        </form>
        <p style="text-align:center"><a href="/">← Voltar para o login</a></p>
    </div>
    </body>
    </html>
    '''

@app.route('/feed')
@login_required
def feed():
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT id, user_nome, texto, curtidas FROM posts ORDER BY tempo DESC")
    posts = c.fetchall()
    conn.close()
    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Feed - Ôio Social</title>
    <style>
        body{{font-family:Arial;background:#f0f2f5;margin:0;padding:20px}}
        .container{{max-width:600px;margin:auto}}
        .card{{background:white;padding:15px;border-radius:10px;margin-bottom:15px}}
        button{{background:#009c3b;color:white;border:none;padding:10px;border-radius:8px;cursor:pointer}}
        textarea{{width:100%;padding:10px;border-radius:8px;margin:5px 0}}
        .header{{background:#009c3b;color:white;padding:15px;border-radius:10px;margin-bottom:20px}}
        a{{color:white;text-decoration:none}}
        .nav a{{margin-left:15px}}
        h3{{margin:0}}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            🇧🇷 Ôio Social
            <div class="nav" style="margin-top:10px">
                <a href="/feed">🏠 Feed</a>
                <a href="/perfil">👤 Perfil</a>
                <a href="/recados">📬 Recados</a>
                <a href="/logout">🚪 Sair</a>
            </div>
        </div>
        <div class="card">
            <h3>Olá, {session['user_nome']}!</h3>
            <form method="POST" action="/postar">
                <textarea name="texto" rows="3" placeholder="O que você quer mostrar hoje?"></textarea>
                <button type="submit">Publicar 🇧🇷</button>
            </form>
        </div>
        <h3>Notícias</h3>
        {''.join([f'<div class="card"><b>{p[1]}</b><p>{p[2]}</p><a href="/curtir/{p[0]}">❤️ Curtir ({p[3]})</a></div>' for p in posts])}
    </div>
    </body>
    </html>
    '''

@app.route('/postar', methods=['POST'])
@login_required
def postar():
    texto = request.form['texto']
    if texto:
        conn = sqlite3.connect('oio.db')
        c = conn.cursor()
        c.execute("INSERT INTO posts (user_id, user_nome, texto) VALUES (?,?,?)",
                  (session['user_id'], session['user_nome'], texto))
        conn.commit()
        conn.close()
        flash('Post publicado!')
    return redirect('/feed')

@app.route('/curtir/<int:post_id>')
@login_required
def curtir(post_id):
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("UPDATE posts SET curtidas = curtidas + 1 WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return redirect('/feed')

@app.route('/perfil')
@login_required
def perfil():
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT nome, apelido, cidade FROM usuarios WHERE id = ?", (session['user_id'],))
    user = c.fetchone()
    conn.close()
    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Perfil - Ôio Social</title>
    <style>
        body{{font-family:Arial;background:#f0f2f5;margin:0;padding:20px}}
        .container{{max-width:600px;margin:auto}}
        .card{{background:white;padding:20px;border-radius:10px;text-align:center}}
        .foto{{width:100px;height:100px;border-radius:50%;background:#009c3b;margin:0 auto;display:flex;align-items:center;justify-content:center;font-size:40px}}
        a{{color:#009c3b;text-decoration:none}}
        button{{background:#009c3b;color:white;border:none;padding:10px;border-radius:8px;cursor:pointer}}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="card">
            <div class="foto">🇧🇷</div>
            <h2>{user[0]}</h2>
            <p>@{user[1]} • {user[2]}</p>
            <a href="/feed">← Voltar ao Feed</a> | <a href="/logout">Sair</a>
        </div>
    </div>
    </body>
    </html>
    '''

@app.route('/recados')
@login_required
def recados():
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT de_user_nome, mensagem, cutucada FROM recados WHERE para_user_id = ? ORDER BY tempo DESC", (session['user_id'],))
    recados = c.fetchall()
    conn.close()
    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Recados - Ôio Social</title>
    <style>
        body{{font-family:Arial;background:#f0f2f5;margin:0;padding:20px}}
        .container{{max-width:600px;margin:auto}}
        .card{{background:white;padding:15px;border-radius:10px;margin-bottom:15px}}
        button{{background:#009c3b;color:white;border:none;padding:10px;border-radius:8px;cursor:pointer}}
        .cutucada{{background:#ffeb3b}}
        input,textarea{{width:100%;padding:10px;margin:5px 0;border-radius:8px}}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="card">
            <h3>Enviar Recado</h3>
            <form method="POST" action="/enviar_recado">
                <input type="text" name="para_apelido" placeholder="Apelido do amigo" required>
                <textarea name="mensagem" rows="2" placeholder="Sua mensagem..."></textarea>
                <button type="submit">📨 Enviar Recado</button>
            </form>
            <hr>
            <a href="/cutucar_todos"><button style="background:#ff9800">👊 Cutucar TODOS os amigos!</button></a>
        </div>
        <h3>Seus Recados</h3>
        {''.join([f'<div class="card {"cutucada" if r[2]==1 else ""}"><b>{r[0]}</b><p>{r[1]}</p></div>' for r in recados])}
        <a href="/feed">← Voltar</a>
    </div>
    </body>
    </html>
    '''

@app.route('/enviar_recado', methods=['POST'])
@login_required
def enviar_recado():
    para_apelido = request.form['para_apelido']
    mensagem = request.form['mensagem']
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT id FROM usuarios WHERE apelido = ?", (para_apelido,))
    user = c.fetchone()
    if user:
        c.execute("INSERT INTO recados (para_user_id, de_user_nome, mensagem) VALUES (?,?,?)",
                  (user[0], session['user_nome'], mensagem))
        conn.commit()
        flash('Recado enviado!')
    else:
        flash('Usuário não encontrado!')
    conn.close()
    return redirect('/recados')

@app.route('/cutucar_todos')
@login_required
def cutucar_todos():
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT id FROM usuarios WHERE id != ?", (session['user_id'],))
    usuarios = c.fetchall()
    for u in usuarios:
        c.execute("INSERT INTO recados (para_user_id, de_user_nome, mensagem, cutucada) VALUES (?,?,?,?)",
                  (u[0], session['user_nome'], f"{session['user_nome']} cutucou TODO MUNDO! 👊", 1))
    conn.commit()
    flash(f'Você cutucou {len(usuarios)} pessoas! Cutucada em massa! 🎉')
    conn.close()
    return redirect('/recados')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
