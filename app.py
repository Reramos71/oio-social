
from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Ôio Social</title></head>
    <body style="background:linear-gradient(135deg,#009c3b,#ffdf00);font-family:Arial;text-align:center;padding:50px">
        <div style="background:white;padding:40px;border-radius:20px;max-width:400px;margin:auto">
            <h1>🇧🇷 Ôio Social</h1>
            <p>Site no ar! 🎉</p>
            <p>Login: admin / admin123</p>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
