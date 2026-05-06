from flask import Flask, request, redirect, session
import os

app = Flask(__name__)
app.secret_key = 'qualquer_coisa'

@app.route('/')
def login():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Ôio Social - Login</title>
        <style>
            body{
                background: linear-gradient(135deg, #009c3b, #ffdf00);
                font-family: Arial;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .box{
                background: white;
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                width: 300px;
            }
            input, button{
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border-radius: 8px;
            }
            button{
                background: #009c3b;
                color: white;
                border: none;
                cursor: pointer;
            }
            h1{ color: #009c3b; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🇧🇷 Ôio Social</h1>
            <form method="POST" action="/logar">
                <input type="text" name="usuario" placeholder="Usuário" required>
                <input type="password" name="senha" placeholder="Senha" required>
                <button type="submit">Entrar</button>
            </form>
            <p>admin / admin123</p>
        </div>
    </body>
    </html>
    '''

@app.route('/logar', methods=['POST'])
def logar():
    usuario = request.form['usuario']
    senha = request.form['senha']
    
    if usuario == 'admin' and senha == 'admin123':
        session['logado'] = True
        return redirect('/feed')
    else:
        return '''
        <h2>Erro! Usuário ou senha incorretos.</h2>
        <a href="/">Voltar</a>
        '''

@app.route('/feed')
def feed():
    if not session.get('logado'):
        return redirect('/')
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Feed - Ôio Social</title>
    <style>
        body{background:#f0f2f5;font-family:Arial;margin:0;padding:20px}
        .header{background:#009c3b;color:white;padding:15px;text-align:center}
        .card{background:white;padding:15px;border-radius:10px;margin:15px 0}
        a{color:#009c3b;text-decoration:none}
    </style>
    </head>
    <body>
        <div class="header">
            <h1>🇧🇷 Ôio Social</h1>
            <a href="/feed">Feed</a> | <a href="/perfil">Perfil</a> | <a href="/sair">Sair</a>
        </div>
        <div class="card">
            <h3>Bem-vindo ao Ôio Social!</h3>
            <p>Rede social brasileira funcionando! 🇧🇷</p>
            <p>Em breve: posts, curtidas, recados e muito mais!</p>
        </div>
    </body>
    </html>
    '''

@app.route('/perfil')
def perfil():
    if not session.get('logado'):
        return redirect('/')
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Perfil</title>
    <style>
        body{background:linear-gradient(135deg,#009c3b,#ffdf00);font-family:Arial;text-align:center;padding:50px}
        .card{background:white;padding:30px;border-radius:20px;max-width:400px;margin:auto}
        .foto{width:100px;height:100px;border-radius:50%;background:#009c3b;margin:auto;display:flex;align-items:center;justify-content:center;font-size:40px}
    </style>
    </head>
    <body>
        <div class="card">
            <div class="foto">🇧🇷</div>
            <h2>Administrador</h2>
            <p>@admin • Brasil</p>
            <a href="/feed">← Voltar</a>
        </div>
    </body>
    </html>
    '''

@app.route('/sair')
def sair():
