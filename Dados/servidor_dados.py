
import json
import threading
from socket import socket, AF_INET, SOCK_STREAM
from pathlib import Path

# Caminho para os arquivos de dados
base_path = Path(__file__).parent
dados_path = base_path

def carregar_dados(nome_arquivo):
    with open(dados_path / nome_arquivo, encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(nome_arquivo, dados):
    with open(dados_path / nome_arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4)

# OPERACOES

def cadastrar_usuario(param):
    usuarios = carregar_dados("usuarios.json")
    novo_id = max([u["id"] for u in usuarios], default=0) + 1
    param["id"] = novo_id
    usuarios.append(param)
    salvar_dados("usuarios.json", usuarios)
    return {"status": "ok", "mensagem": "Usuário cadastrado com sucesso", "id": novo_id}

def autenticar_usuario(param):
    usuarios = carregar_dados("usuarios.json")
    for u in usuarios:
        if u["email"] == param["email"] and u["senha"] == param["senha"]:
            return {"status": "ok", "usuario": u}
    return {"status": "erro", "mensagem": "Usuário ou senha inválidos"}

def buscar_usuario(param):
    usuarios = carregar_dados("usuarios.json")
    for u in usuarios:
        if u["id"] == param["id"]:
            return {"status": "ok", "usuario": u}
    return {"status": "erro", "mensagem": "Usuário não encontrado"}

def cadastrar_produto(param):
    produtos = carregar_dados("produtos.json")
    novo_id = max([p["id"] for p in produtos], default=0) + 1
    param["id"] = novo_id
    produtos.append(param)
    salvar_dados("produtos.json", produtos)
    return {"status": "ok", "mensagem": "Produto cadastrado", "id": novo_id}

def listar_produtos(param):
    produtos = carregar_dados("produtos.json")
    return {"status": "ok", "produtos": produtos}

def buscar_produto(param):
    produtos = carregar_dados("produtos.json")
    for p in produtos:
        if p["id"] == param["id"]:
            return {"status": "ok", "produto": p}
    return {"status": "erro", "mensagem": "Produto não encontrado"}

def comprar_produto(param):
    produtos = carregar_dados("produtos.json")
    compras = carregar_dados("compras.json")

    for produto in produtos:
        if produto["id"] == param["produto_id"]:
            if produto["estoque"] >= param["quantidade"]:
                produto["estoque"] -= param["quantidade"]
                nova_compra = {
                    "cliente_id": param["cliente_id"],
                    "produto_id": param["produto_id"],
                    "quantidade": param["quantidade"]
                }
                compras.append(nova_compra)
                salvar_dados("produtos.json", produtos)
                salvar_dados("compras.json", compras)
                return {"status": "ok", "mensagem": "Compra realizada com sucesso"}
            else:
                return {"status": "erro", "mensagem": "Estoque insuficiente"}
    return {"status": "erro", "mensagem": "Produto não encontrado"}

def listar_compras_cliente(param):
    compras = carregar_dados("compras.json")
    cliente_compras = [c for c in compras if c["cliente_id"] == param["cliente_id"]]
    return {"status": "ok", "compras": cliente_compras}

# SERVIDOR SOCKET 

OPERACOES = {
    "cadastrar_usuario": cadastrar_usuario,
    "autenticar_usuario": autenticar_usuario,
    "buscar_usuario": buscar_usuario,
    "cadastrar_produto": cadastrar_produto,
    "listar_produtos": listar_produtos,
    "buscar_produto": buscar_produto,
    "comprar_produto": comprar_produto,
    "listar_compras_cliente": listar_compras_cliente
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