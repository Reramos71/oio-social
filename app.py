from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import random
import string
from functools import wraps
import requests

app = Flask(__name__)
app.secret_key = 'oio_social_chave_secreta_2025'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# Configurações do SendGrid (pegam as variáveis que você configurou no Render)
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
MAIL_FROM = os.environ.get('MAIL_FROM', 'renatobarbososo@hotmail.com')

def enviar_email(para, assunto, conteudo):
    """Envia email usando API do SendGrid"""
    if not SENDGRID_API_KEY:
        print("ERRO: SENDGRID_API_KEY não configurada")
        return False
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "personalizations": [{"to": [{"email": para}]}],
        "from": {"email": MAIL_FROM},
        "subject": assunto,
        "content": [{"type": "text/html", "value": conteudo}]
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 202:
            print(f"Email enviado para {para}")
            return True
        else:
            print(f"Erro ao enviar email: {response.status_code}")
            return False
    except Exception as e:
        print(f"Exceção ao enviar email: {e}")
        return False

def gerar_senha_aleatoria(tamanho=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Faça login primeiro')
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        apelido TEXT,
        data_nascimento TEXT,
        cidade TEXT,
        estado TEXT,
        endereco_perfil TEXT,
        estado_civil TEXT,
        interesse TEXT,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        foto_perfil TEXT,
        humor TEXT DEFAULT 'Feliz',
        is_admin INTEGER DEFAULT 0,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        user_nome TEXT,
        user_foto TEXT,
        texto TEXT,
        imagem TEXT,
        curtidas INTEGER DEFAULT 0,
        tempo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES usuarios(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS comentarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER,
        user_id INTEGER,
        user_nome TEXT,
        texto TEXT,
        tempo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES usuarios(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS recados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        para_user_id INTEGER,
        de_user_id INTEGER,
        de_user_nome TEXT,
        mensagem TEXT,
        lido INTEGER DEFAULT 0,
        cutucada INTEGER DEFAULT 0,
        tempo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (para_user_id) REFERENCES usuarios(id),
        FOREIGN KEY (de_user_id) REFERENCES usuarios(id)
    )''')
    
    c.execute("SELECT * FROM usuarios WHERE email = 'admin@oio.com'")
    if not c.fetchone():
        c.execute('''INSERT INTO usuarios (nome, apelido, email, senha, is_admin, cidade, estado)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  ('Administrador', 'admin', 'admin@oio.com', generate_password_hash('admin123'), 1, 'Brasil', 'BR'))
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    senha = request.form['senha']
    
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT id, nome, senha, is_admin, foto_perfil, apelido, cidade, estado FROM usuarios WHERE email = ? OR apelido = ?", (username, username))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[2], senha):
        session['user_id'] = user[0]
        session['user_nome'] = user[1]
        session['is_admin'] = user[3]
        session['foto_perfil'] = user[4] or 'default.png'
        session['apelido'] = user[5]
        session['cidade'] = user[6]
        session['estado'] = user[7]
        return redirect('/feed')
    else:
        flash('Usuário ou senha incorretos')
        return redirect('/')

@app.route('/esqueci_senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('oio.db')
        c = conn.cursor()
        c.execute("SELECT id, nome FROM usuarios WHERE email = ?", (email,))
        user = c.fetchone()
        
        if user:
            nova_senha = gerar_senha_aleatoria()
            senha_hash = generate_password_hash(nova_senha)
            c.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, user[0]))
            conn.commit()
            
            # Enviar email
            html = f"""
            <h2>🇧🇷 Ôio Social - Recuperação de Senha</h2>
            <p>Olá {user[1]}!</p>
            <p>Você solicitou a recuperação de senha. Sua nova senha é:</p>
            <h3 style="background:#ffdf00;padding:10px;display:inline-block;border-radius:5px">{nova_senha}</h3>
            <p>Recomendamos trocar sua senha após o login.</p>
            <a href="https://oio-social.onrender.com/">Clique aqui para fazer login</a>
            <p>Se você não solicitou esta alteração, ignore este email.</p>
            <hr>
            <p>Ôio Social - A rede social brasileira 🇧🇷</p>
            """
            if enviar_email(email, "Ôio Social - Nova Senha", html):
                flash('Uma nova senha foi enviada para seu email!')
            else:
                flash('Erro ao enviar email. Tente novamente mais tarde.')
        else:
            flash('Email não encontrado!')
        conn.close()
        return redirect('/')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Recuperar Senha - Ôio Social</title>
    <style>
        body{background:linear-gradient(135deg,#009c3b,#ffdf00);font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh}
        .box{background:white;padding:40px;border-radius:20px;text-align:center;width:350px}
        input,button{width:100%;padding:12px;margin:10px 0;border-radius:8px;border:1px solid #ddd}
        button{background:#009c3b;color:white;border:none;cursor:pointer;font-weight:bold}
        a{color:#009c3b}
        h1{color:#009c3b}
    </style>
    </head>
    <body>
    <div class="box">
        <h1>🇧🇷 Recuperar Senha</h1>
        <form method="POST">
            <input type="email" name="email" placeholder="Digite seu email" required>
            <button type="submit">Enviar nova senha</button>
        </form>
        <p><a href="/">← Voltar para o login</a></p>
    </div>
    </body>
    </html>
    '''

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        apelido = request.form['apelido']
        data_nascimento = request.form['data_nascimento']
        cidade = request.form['cidade']
        estado = request.form['estado']
        endereco_perfil = request.form.get('endereco_perfil', '')
        estado_civil = request.form.get('estado_civil', '')
        interesse = request.form.get('interesse', '')
        email = request.form['email']
        senha_hash = generate_password_hash(request.form['senha'])
        
        foto_perfil = None
        if 'foto_perfil' in request.files:
            file = request.files['foto_perfil']
            if file and file.filename:
                filename = secure_filename(f"{email}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                foto_perfil = filename
        
        conn = sqlite3.connect('oio.db')
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO usuarios 
                        (nome, apelido, data_nascimento, cidade, estado, endereco_perfil, estado_civil, interesse, email, senha, foto_perfil) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (nome, apelido, data_nascimento, cidade, estado, endereco_perfil, estado_civil, interesse, email, senha_hash, foto_perfil))
            conn.commit()
            flash('Conta criada com sucesso! Faça login.')
            return redirect('/')
        except sqlite3.IntegrityError:
            flash('Email já cadastrado!')
        finally:
            conn.close()
    
    return render_template('cadastro.html')

@app.route('/feed')
@login_required
def feed():
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute('''SELECT p.id, p.user_nome, p.texto, p.imagem, p.curtidas, p.tempo, u.foto_perfil,
                        (SELECT COUNT(*) FROM comentarios WHERE post_id = p.id) as total_comentarios
                 FROM posts p
                 LEFT JOIN usuarios u ON p.user_id = u.id
                 ORDER BY p.tempo DESC''')
    posts = c.fetchall()
    conn.close()
    return render_template('feed.html', posts=posts, user_nome=session['user_nome'], user_foto=session.get('foto_perfil', 'default.png'))

@app.route('/postar', methods=['POST'])
@login_required
def postar():
    texto = request.form['texto']
    imagem = request.files.get('imagem')
    imagem_nome = None
    
    if imagem and imagem.filename:
        filename = secure_filename(f"{session['user_id']}_{imagem.filename}")
        imagem.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagem_nome = filename
    
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("INSERT INTO posts (user_id, user_nome, texto, imagem) VALUES (?, ?, ?, ?)",
              (session['user_id'], session['user_nome'], texto, imagem_nome))
    conn.commit()
    conn.close()
    
    flash('Post publicado! 🇧🇷')
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
    c.execute("SELECT * FROM usuarios WHERE id = ?", (session['user_id'],))
    usuario = c.fetchone()
    
    c.execute("SELECT * FROM posts WHERE user_id = ? ORDER BY tempo DESC", (session['user_id'],))
    posts = c.fetchall()
    
    c.execute("SELECT * FROM recados WHERE para_user_id = ? ORDER BY tempo DESC LIMIT 10", (session['user_id'],))
    recados = c.fetchall()
    conn.close()
    
    return render_template('perfil.html', usuario=usuario, posts=posts, recados=recados)

@app.route('/editar_humor', methods=['POST'])
@login_required
def editar_humor():
    humor = request.form['humor']
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("UPDATE usuarios SET humor = ? WHERE id = ?", (humor, session['user_id']))
    conn.commit()
    conn.close()
    flash('Humor atualizado!')
    return redirect('/perfil')

@app.route('/recados')
@login_required
def recados():
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute('''SELECT r.*, u.foto_perfil 
                 FROM recados r
                 LEFT JOIN usuarios u ON r.de_user_id = u.id
                 WHERE r.para_user_id = ? 
                 ORDER BY r.tempo DESC''', (session['user_id'],))
    recados_lista = c.fetchall()
    
    conn.close()
    return render_template('recados.html', recados=recados_lista)

@app.route('/enviar_recado', methods=['POST'])
@login_required
def enviar_recado():
    mensagem = request.form['mensagem']
    para_apelido = request.form['para_apelido']
    
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT id, nome FROM usuarios WHERE apelido = ?", (para_apelido,))
    usuario = c.fetchone()
    
    if usuario:
        c.execute("""INSERT INTO recados (para_user_id, de_user_id, de_user_nome, mensagem) 
                     VALUES (?, ?, ?, ?)""",
                  (usuario[0], session['user_id'], session['user_nome'], mensagem))
        conn.commit()
        flash(f'Recado enviado para {usuario[1]}!')
    else:
        flash('Usuário não encontrado!')
    
    conn.close()
    return redirect('/recados')

@app.route('/cutucar/<int:user_id>')
@login_required
def cutucar(user_id):
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT nome FROM usuarios WHERE id = ?", (user_id,))
    usuario = c.fetchone()
    
    if usuario:
        c.execute("""INSERT INTO recados (para_user_id, de_user_id, de_user_nome, mensagem, cutucada) 
                     VALUES (?, ?, ?, ?, ?)""",
                  (user_id, session['user_id'], session['user_nome'], f"{session['user_nome']} te cutucou! 👊", 1))
        conn.commit()
        flash(f'Você cutucou {usuario[0]}!')
    
    conn.close()
    return redirect('/recados')

@app.route('/cutucar_todos')
@login_required
def cutucar_todos():
    conn = sqlite3.connect('oio.db')
    c = conn.cursor()
    c.execute("SELECT id, nome FROM usuarios WHERE id != ?", (session['user_id'],))
    usuarios = c.fetchall()
    
    for usuario in usuarios:
        c.execute("""INSERT INTO recados (para_user_id, de_user_id, de_user_nome, mensagem, cutucada) 
                     VALUES (?, ?, ?, ?, ?)""",
                  (usuario[0], session['user_id'], session['user_nome'], f"{session['user_nome']} cutucou TODO MUNDO! 👊👊👊", 1))
    conn.commit()
    flash(f'Você cutucou {len(usuarios)} pessoas! Cutucada em massa! 🎉')
    conn.close()
    return redirect('/recados')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=True)
