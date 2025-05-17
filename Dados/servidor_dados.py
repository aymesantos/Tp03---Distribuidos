import json
import threading
from socket import socket, AF_INET, SOCK_STREAM
from banco_dados import *
from datetime import datetime

# OPERACOES

def cadastrar_usuario(param):
    nome = param.get("nome")
    email = param.get("email")
    senha = param.get("senha")
    tipo = param.get("tipo", "cliente")
    return cadastrar_usuario_sqlite(nome, email, senha, tipo)

def cadastrar_usuario_sqlite(nome, email, senha, tipo):
    return cadastrar_usuario(nome, email, senha, tipo)

def autenticar_usuario(param):
    email = param.get("email")
    senha = param.get("senha")
    return autenticar_usuario_sqlite(email, senha)

def autenticar_usuario_sqlite(email, senha):
    return autenticar_usuario(email, senha)

def buscar_usuario(param):
    usuario_id = param.get("id")
    return buscar_usuario_sqlite(usuario_id)

def buscar_usuario_sqlite(usuario_id):
    return buscar_usuario(usuario_id)

def cadastrar_loja(param):
    nome = param.get("nome")
    descricao = param.get("descricao")
    usuario_id = param.get("usuario_id")
    return cadastrar_loja(nome, descricao, usuario_id)

def listar_lojas(param):
    return listar_lojas()

def buscar_loja(param):
    loja_id = param.get("id")
    return buscar_loja(loja_id)

def cadastrar_produto(param):
    nome = param.get("nome")
    descricao = param.get("descricao")
    preco = param.get("preco")
    estoque = param.get("estoque")
    loja_id = param.get("loja_id")
    return cadastrar_produto_sqlite(nome, descricao, preco, estoque, loja_id)

def cadastrar_produto_sqlite(nome, descricao, preco, estoque, loja_id):
    return cadastrar_produto(nome, descricao, preco, estoque, loja_id)

def listar_produtos(param):
    return listar_produtos()

def buscar_produto(param):
    produto_id = param.get("id")
    return buscar_produto(produto_id)

def comprar_produto(param):
    usuario_id = param.get("cliente_id")
    itens = param.get("itens")  # lista de dicionários: produto_id, quantidade, preco_unitario
    data = datetime.now().isoformat()
    status = "realizada"
    return registrar_compra(usuario_id, data, status, itens)

def listar_compras_cliente(param):
    usuario_id = param.get("cliente_id")
    return listar_compras_usuario(usuario_id)

def registrar_avaliacao_op(param):
    usuario_id = param.get("usuario_id")
    produto_id = param.get("produto_id")
    nota = param.get("nota")
    comentario = param.get("comentario")
    data = datetime.now().isoformat()
    return registrar_avaliacao(usuario_id, produto_id, nota, comentario, data)

def listar_avaliacoes_produto_op(param):
    produto_id = param.get("produto_id")
    return listar_avaliacoes_produto(produto_id)

# SERVIDOR SOCKET 

OPERACOES = {
    "cadastrar_usuario": cadastrar_usuario,
    "autenticar_usuario": autenticar_usuario,
    "buscar_usuario": buscar_usuario,
    "cadastrar_loja": cadastrar_loja,
    "listar_lojas": listar_lojas,
    "buscar_loja": buscar_loja,
    "cadastrar_produto": cadastrar_produto,
    "listar_produtos": listar_produtos,
    "buscar_produto": buscar_produto,
    "comprar_produto": comprar_produto,
    "listar_compras_cliente": listar_compras_cliente,
    "registrar_avaliacao": registrar_avaliacao_op,
    "listar_avaliacoes_produto": listar_avaliacoes_produto_op
}

def tratar_cliente(conexao, endereco):
    with conexao:
        try:
            dados = conexao.recv(4096)
            requisicao = json.loads(dados.decode())
            operacao = requisicao.get("operacao")
            parametros = requisicao.get("parametros", {})
            if operacao in OPERACOES:
                resposta = OPERACOES[operacao](parametros)
            else:
                resposta = {"status": "erro", "mensagem": "Operação desconhecida"}
        except Exception as e:
            resposta = {"status": "erro", "mensagem": str(e)}

        conexao.sendall(json.dumps(resposta).encode())

def iniciar_servidor(host='localhost', porta=5003):
    with socket(AF_INET, SOCK_STREAM) as servidor:
        servidor.bind((host, porta))
        servidor.listen()
        print(f"Servidor de dados escutando em {host}:{porta}...")
        while True:
            conn, addr = servidor.accept()
            threading.Thread(target=tratar_cliente, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    iniciar_servidor()