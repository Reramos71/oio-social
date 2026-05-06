from flask import Flask, request, redirect, session, flash, render_template_string
import os

app = Flask(__name__)
app.secret_key = 'oio_social_secret_key'

# Página de Login
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ôio Social</title>
        <style>
            body{background:linear-gradient(135deg,#009c3b,#ffdf00);font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
            .box{background:white;padding:40px;border-radius:20px;text-align:center;width:350px}
            input,button{width:100%;padding:12px;margin:10px 0;border-radius:8px}
            button{background:#009c3b;color:white;border:none;cursor:pointer}
            h1{color:#009c3b}
        </style>
    </head>
    <body>
    <div class="box">
        <h1>🇧🇷 Ôio Social</h1>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Usuário" required>
            <input type="password" name="senha" placeholder="Senha" required>
            <button type="submit">Entrar</button>
        </form>
        <p>admin / admin123</p>
    </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['POST'])
def login():
    user = request.form['username']
    pwd = request.form['senha']
    
    if user == 'admin' and pwd == 'admin123':
        session['user'] = user
        return redirect('/feed')
    else:
        flash('Usuário ou senha incorretos')
        return redirect('/')

@app.route('/feed')
def feed():
    if 'user' not in session:
        return redirect('/')
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Ôio Social - Feed</title>
    <style>
        body{background:#f0f2f5;font-family:Arial;margin:0;padding:20px}
        .container{max-width:600px;margin:auto}
        .card{background:white;padding:20px;border-radius:10px;margin-bottom:15px}
        .header{background:#009c3b;color:white;padding:15px;border-radius:10px;margin-bottom:20px}
        a{color:white;text-decoration:none;margin:0 10px}
        textarea{width:100%;padding:10px;border-radius:8px;margin:10px 0}
        button{background:#009c3b;color:white;border:none;padding:10px;border-radius:8px;cursor:pointer}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <div style="display:flex;justify-content:space-between">
                <h2>🇧🇷 Ôio Social</h2>
                <div>
                    <a href="/feed">🏠 Feed</a>
                    <a href="/perfil">👤 Perfil</a>
                    <a href="/logout">🚪 Sair</a>
                </div>
            </div>
        </div>
        <div class="card">
            <h3>Bem-vindo, admin!</h3>
            <p>Ôio Social está no ar! 🇧🇷</p>
            <p>Em breve: posts, recados, perfil completo, fotos e muito mais!</p>
        </div>
    </div>
    </body>
    </html>
    '''

@app.route('/perfil')
def perfil():
    if 'user' not in session:
        return redirect('/')
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Perfil - Ôio Social</title>
    <style>
        body{background:linear-gradient(135deg,#009c3b,#ffdf00);font-family:Arial;margin:0;padding:20px}
        .container{max-width:500px;margin:auto}
        .card{background:white;padding:30px;border-radius:20px;text-align:center}
        .foto{width:120px;height:120px;border-radius:50%;background:#009c3b;margin:0 auto;display:flex;align-items:center;justify-content:center;font-size:50px}
        h2{color:#009c3b}
        a{color:#009c3b;text-decoration:none}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="card">
            <div class="foto">🇧🇷</div>
            <h2>Administrador</h2>
            <p>@admin • Brasil</p>
            <a href="/feed">← Voltar ao Feed</a> | <a href="/logout">Sair</a>
        </div>
    </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
