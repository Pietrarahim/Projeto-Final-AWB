from flask import Flask, render_template, request, redirect, session, flash, url_for, Blueprint
import json
import os
from werkzeug.utils import secure_filename
import requests
#-------------- Cria um Blueprint para as rotas

front_controller = Blueprint('front_controller', __name__)

#-------------Definindo diretórios e arquivos de configuração

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "model", "data", "dados.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "image")

#------------------ Tipos de imagens permitidas

TIPOS_IMAGEM = set(['png', 'jpg', 'jpeg', 'gif'])

#---------------- Funções auxiliares ----------------------#

# Carregar dados do arquivo JSON
def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

# Salvar dados no arquivo JSON
def salvar_dados(ingressos):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)  # Cria o diretório, se não existir
    with open(DATA_FILE, 'w') as f:
        json.dump(ingressos, f, indent=4)

# Validar a extensão da imagem
def validar_imagem(foto):
    # Obtendo a extensão do arquivo
    extensao = foto.filename.split('.')[-1].lower()
    if extensao not in TIPOS_IMAGEM:
        flash("Tipo de imagem inválido! Apenas PNG, JPG, JPEG e GIF são permitidos.")
        return False
    return True


#----------------- Rota para visualizar e gerenciar ingressos
@front_controller.route('/festas')
def festas():
    ingressos = carregar_dados()
    return render_template("festas.html", ingressos=ingressos)

#-------------------- Função para adicionar ingresso ao carrinho
@front_controller.route('/adicionar_ingresso', methods=["POST"])
def adicionar_ingresso():
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    email = request.form.get('email')
    quantidade = int(request.form.get('quantidade'))
    foto = request.files['foto']

    if foto and validar_imagem(foto):
        foto_filename = secure_filename(foto.filename)
        caminho_foto = os.path.join(UPLOAD_FOLDER, foto_filename)

        # Garante que o diretório de uploads exista
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Salva a foto
        foto.save(caminho_foto)

        # Carrega dados e adiciona o ingresso
        ingressos = carregar_dados()
        ingresso = {
            'id': len(ingressos) + 1,  # Simula um ID único
            'nome': nome,
            'telefone': telefone,
            'email': email,
            'quantidade': quantidade,
            'foto': caminho_foto
        }

        ingressos.append(ingresso)
        salvar_dados(ingressos)
        flash('Ingresso adicionado ao carrinho!')
    else:
        flash("Erro ao adicionar ingresso. Verifique os dados e tente novamente.")
    
    return redirect(url_for('festas'))

#---------------- Função para remover ingresso do carrinho
@front_controller.route('/remover_ingresso/<int:ingresso_id>', methods=["POST"])
def remover_ingresso(ingresso_id):
    ingressos = carregar_dados()
    ingressos = [ingresso for ingresso in ingressos if ingresso['id'] != ingresso_id]
    salvar_dados(ingressos)
    flash('Ingresso removido do carrinho!')
    return redirect(url_for('festas'))

#-------------------Função para finalizar a compra
@front_controller.route('/finalizar_compra', methods=["POST"])
def finalizar_compra():
    ingressos = carregar_dados()

    # Se o carrinho estiver vazio
    if not ingressos:
        flash("Seu carrinho está vazio. Adicione ingressos antes de finalizar a compra.")
        return redirect(url_for('festas'))

    # simular a conclusão da compra (por exemplo, limpar o carrinho)
    salvar_dados([])  # Limpar os ingressos após a compra

    flash("Compra finalizada com sucesso!")
    return redirect(url_for('festas'))