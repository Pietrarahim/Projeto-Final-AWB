from flask import Flask, render_template, request, redirect, session, flash, url_for
import json
import os
from werkzeug.utils import secure_filename
import requests
from controllers.front_controller import front_controller

# Definindo diretórios e arquivos de configuração
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "model", "data", "dados.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "image")

# Tipos de imagens permitidas
TIPOS_IMAGEM = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)


#----------------- Registra o Blueprint
app.register_blueprint(front_controller)

#---------------- Criação da chave secreta ------------------#
app.secret_key = "inter"

#---------------- Rotas principais ------------------------#

# ------------------- Rota principal (Página inicial)
@app.route('/')
def principal():
    return render_template("principal.html")

#-------------------------- Rota de login
def load_users():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)["users"]
    except FileNotFoundError:
        return []

# salvar os usuários no JSON
def save_users(users):
    with open('users.json', 'w') as file:
        json.dump({"users": users}, file, indent=4)

@app.route('/login')
def login():
    return render_template("login.html")

#----------------------- Autenticação do usuário
@app.route('/autenticar', methods=["POST"])
def autenticar():
    email = request.form.get('textEmail')
    senha = request.form.get('textSenha')

    users = load_users()

    for user in users:
        if user['email'] == email and user['password'] == senha:
            session['usuarioLogado'] = email
            flash('Usuário logado com sucesso!')
            return redirect(url_for('principal'))

    flash('Erro de login. Verifique as credenciais.')
    return redirect(url_for('login.html'))
#------------------------------registrar
@app.route('/registrar', methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        email = request.form.get('textEmail')
        senha = request.form.get('textSenha')

        users = load_users()

        # Verifica se o usuário já está registrado
        for user in users:
            if user['email'] == email:
                flash('Email já registrado. Tente outro!')
                return redirect(url_for('registrar'))

        # Registra o novo usuário
        users.append({'email': email, 'password': senha})
        save_users(users)
        flash('Usuário registrado com sucesso! Faça login.')
        return redirect(url_for('login'))

    return render_template('registrar.html')

#---------------------------------------------Logout
@app.route('/sair', methods=["GET","POST"])
def sair():
    session.pop('usuarioLogado', None)
    flash('Usuário deslogado com sucesso!')
    return redirect(url_for('principal'))

#-----------------------Rota para a página de publicações (republi,feminina e masculina)
@app.route('/republi')
def republi():
    return render_template("republi.html")

@app.route('/feminina')
def feminina():
    return render_template("feminina.html")

@app.route('/masculina')
def masculina():
    return render_template("masculina.html")

#---------------------- Rota de comentários, API externa
@app.route('/comentario')
def comentario():
    api_url = "https://dummyapi.io/data/v1/user?limit=10"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        comentarios = response.json()
    except requests.exceptions.RequestException as e:
        flash(f"Erro ao acessar a API: {e}")
        comentarios = []

    return render_template("comentario.html", comentarios=comentarios)


#---------------- Início da aplicação ----------------------#

if __name__ == "__main__":
    app.run(debug=True)
