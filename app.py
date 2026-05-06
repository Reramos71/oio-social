from flask import Flask, request, redirect, session
import os

app = Flask(__name__)
app.secret_key = 'oio_social_key_2025'

# Rota principal - página de login
@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Ôio Social</title>
        <style>
            body {
                background: linear-gradient(135deg, #009c3b, #ffdf00);
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .box {
                background: white;
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                max-width: 400px;
                width: 90%;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border-radius: 8px;
                border: 1px solid #ccc;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #009c3b;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            }
            h1 { color: #009c3b; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🇧🇷 Ôio Social</h1>
            <form method="POST" action="/login">
                <input type="text" name="username" placeholder="Usuário" required>
                <input type="password" name="password" placeholder="Senha" required>
                <button type="submit">Entrar</button>
            </form>
            <p style="margin-top:20px">admin / admin123</p>
        </div>
    </body>
    </html>
    '''

# Rota de login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username == 'admin' and password == 'admin123':
        session['user'] = username
        return redirect('/feed')
    else:
        return '<h2>Erro! Usuário ou senha incorretos. <a href="/">Voltar</a></h2>'

# Rota do feed (após login)
@app.route('/feed')
def feed():
    if 'user' not in session:
        return redirect('/')
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Feed - Ôio Social</title>
        <style>
            body {
                background: #f0f2f5;
                font-family: Arial;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 600px;
                margin: auto;
            }
            .card {
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
            }
            .header {
                background: #009c3b;
                color: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
            }
            button {
                background: #009c3b;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 8px;
                cursor: pointer;
            }
            a { color: white; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                🇧🇷 Ôio Social
                <a href="/perfil" style="float:right">Perfil</a>
                <a href="/logout" style="float:right;margin-right:15px">Sair</a>
            </div>
            <div class="card">
                <h3>Bem-vindo ao Ôio Social!</h3>
                <p>Rede social brasileira no ar! 🇧🇷</p>
                <p>Em breve: posts, recados, curtidas e muito mais!</p>
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
        body{background:linear-gradient(135deg,#009c3b,#ffdf00);font-family:Arial;text-align:center;padding:50px}
        .card{background:white;padding:40px;border-radius:20px;max-width:400px;margin:auto}
        .foto{width:100px;height:100px;border-radius:50%;background:#009c3b;margin:auto;display:flex;align-items:center;justify-content:center;font-size:40px}
    </style>
    </head>
    <body>
        <div class="card">
            <div class="foto">🇧🇷</div>
            <h2>Administrador</h2>
            <p>@admin • Brasil</p>
            <a href="/feed">← Voltar</a> | <a href="/logout">Sair</a>
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
