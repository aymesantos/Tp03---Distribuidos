import sqlite3
import hashlib
import base64
import os
import socket
import json

SERVIDOR_DADOS_HOST = 'localhost'
SERVIDOR_DADOS_PORTA = 5003

def enviar_para_servidor_dados(operacao, parametros):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVIDOR_DADOS_HOST, SERVIDOR_DADOS_PORTA))
            mensagem = json.dumps({"operacao": operacao, "parametros": parametros})
            s.sendall(mensagem.encode())
            resposta = s.recv(4096)
            return json.loads(resposta.decode())
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

def fazer_login(email, senha):
    return enviar_para_servidor_dados("autenticar_usuario", {"email": email, "senha": senha})

def fazer_cadastro(nome, casa, email, senha, tipo_bruxo):
    return enviar_para_servidor_dados("cadastrar_usuario", {
        "nome": nome,
        "email": email,
        "senha": senha,
        "tipo": tipo_bruxo
    })

def obter_perfil(email):
    return enviar_para_servidor_dados("buscar_usuario", {"id": email})

def atualizar_perfil(nome, casa_hogwarts, tipo_bruxo, email):
    # Não existe operação direta no servidor_dados, seria necessário implementar
    return {"status": "erro", "mensagem": "Operação não implementada no servidor de dados."}

def criar_loja(email, nome_loja, descricao):
    return enviar_para_servidor_dados("cadastrar_loja", {
        "nome": nome_loja,
        "descricao": descricao,
        "usuario_id": email
    })

def editar_loja(email, nome_loja, descricao):
    # Não existe operação direta, seria necessário implementar
    return {"status": "erro", "mensagem": "Operação não implementada no servidor de dados."}

def obter_loja(email):
    return enviar_para_servidor_dados("buscar_loja", {"id": email})

def criar_produto(email, nome, descricao, preco, categoria, imagens_base64):
    return enviar_para_servidor_dados("cadastrar_produto", {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": 10,  # Estoque fixo apenas como exemplo
        "loja_id": email
    })

def editar_produto(produto_id, nome, descricao, preco, categoria, status, imagem_base64):
    # Não existe operação direta, seria necessário implementar
    return {"status": "erro", "mensagem": "Operação não implementada no servidor de dados."}

def listar_produtos(filtros=None):
    return enviar_para_servidor_dados("listar_produtos", {})

def listar_meus_produtos(email):
    return enviar_para_servidor_dados("listar_produtos", {})

def obter_produto(id_produto):
    return enviar_para_servidor_dados("buscar_produto", {"id": id_produto})

def adicionar_ao_carrinho(email, produto_id, quantidade=1):
    # Não existe operação direta, seria necessário implementar
    return {"status": "erro", "mensagem": "Operação não implementada no servidor de dados."}

def remover_do_carrinho(id_produto):
    return {"status": "erro", "mensagem": "Operação não implementada no servidor de dados."}

def visualizar_carrinho(email):
    return {"status": "erro", "mensagem": "Operação não implementada no servidor de dados."}

def finalizar_compra(email):
    return enviar_para_servidor_dados("comprar_produto", {"cliente_id": email, "itens": []})

def historico_compras(email):
    return enviar_para_servidor_dados("listar_compras_cliente", {"cliente_id": email})

def historico_vendas(email):
    return {"status": "erro", "mensagem": "Operação não implementada no servidor de dados."}
