import json
import threading
from socket import socket, AF_INET, SOCK_STREAM
from banco_dados import *
from datetime import datetime

# OPERACOES

def cadastrar_usuario_op(param):
    nome = param.get("nome")
    email = param.get("email")
    senha = param.get("senha")
    tipo = param.get("tipo")
    casa = param.get("casa")
    return cadastrar_usuario_sqlite(nome, email, senha, tipo, casa)

def cadastrar_usuario_sqlite(nome, email, senha, tipo, casa):
    return cadastrar_usuario(nome, email, senha, tipo, casa)

def autenticar_usuario_op(param):
    email = param.get("email")
    senha = param.get("senha")
    return autenticar_usuario_sqlite(email, senha)

def autenticar_usuario_sqlite(email, senha):
    return autenticar_usuario(email, senha)

def buscar_usuario(param):
    usuario_id = param.get("id")
    email = param.get("email")
    if usuario_id is not None:
        return buscar_usuario_sqlite(usuario_id)
    elif email is not None:
        return buscar_usuario_por_email(email)
    else:
        return {"status": "erro", "mensagem": "Parâmetro id ou email não fornecido"}

def buscar_usuario_sqlite(usuario_id):
    return buscar_usuario(usuario_id)

def cadastrar_loja(param):
    nome = param.get("nome")
    descricao = param.get("descricao")
    usuario_id = param.get("usuario_id")
    return cadastrar_loja_db(nome, descricao, usuario_id)

def listar_lojas(param):
    return listar_lojas_db(param)

def buscar_loja(param):
    loja_id = param.get("id")
    return buscar_loja(loja_id)

def cadastrar_produto(param):
    nome = param.get("nome")
    descricao = param.get("descricao")
    preco = param.get("preco")
    estoque = param.get("estoque")
    loja_id = param.get("loja_id")
    categoria = param.get("categoria")
    return cadastrar_produto_db(nome, descricao, preco, estoque, loja_id, categoria)

def cadastrar_produto_sqlite(nome, descricao, preco, estoque, loja_id):
    return cadastrar_produto(nome, descricao, preco, estoque, loja_id)

def listar_produtos(param):
    return listar_produtos_db(param)

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

def listar_vendas_vendedor_op(param):
    usuario_id = param.get("usuario_id")
    return listar_vendas_vendedor(usuario_id)

def editar_produto_op(param):
    produto_id = param.get("id")
    nome = param.get("nome")
    descricao = param.get("descricao")
    preco = param.get("preco")
    estoque = param.get("estoque")
    return editar_produto(produto_id, nome, descricao, preco, estoque)

def adicionar_produto_carrinho_op(param):
    email = param.get("email")
    produto_id = param.get("produto_id")
    quantidade = param.get("quantidade", 1)
    return adicionar_produto_carrinho(email, produto_id, quantidade)

def visualizar_carrinho_op(param):
    email = param.get("email")
    return visualizar_carrinho(email)

def remover_produto_carrinho_op(param):
    email = param.get("email")
    produto_id = param.get("produto_id")
    return remover_produto_carrinho(email, produto_id)

# SERVIDOR SOCKET 

OPERACOES = {
    "cadastrar_usuario": cadastrar_usuario_op,
    "autenticar_usuario": autenticar_usuario_op,
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
    "listar_avaliacoes_produto": listar_avaliacoes_produto_op,
    "listar_vendas_vendedor": listar_vendas_vendedor_op,
    "editar_produto": editar_produto_op,
    "adicionar_produto_carrinho": adicionar_produto_carrinho_op,
    "visualizar_carrinho": visualizar_carrinho_op,
    "remover_produto_carrinho": remover_produto_carrinho_op
}

def tratar_cliente(conexao, endereco):
    print(f"[DADOS] Conexão recebida de {endereco}")
    with conexao:
        try:
            dados = conexao.recv(4096)
            print(f"[DEBUG] Dados recebidos: {dados}")
            requisicao = json.loads(dados.decode())
            print(f"[DEBUG] Requisição decodificada: {requisicao}")
            operacao = requisicao.get("operacao")
            parametros = requisicao.get("parametros", {})
            print(f"[DEBUG] Operação: {operacao}, Parâmetros: {parametros}")
            if operacao in OPERACOES:
                resposta = OPERACOES[operacao](parametros)
            else:
                resposta = {"status": "erro", "mensagem": "Operação desconhecida"}
        except Exception as e:
            print(f"[DEBUG] Exceção no tratar_cliente: {e}")
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