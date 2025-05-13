import socket
import json

# Mock de dados
usuarios = {
    "ayme@gmail.com": {
        "senha": "senha123",
        "nome": "Ayme Faustino",
        "casa": "Grifinória",
        "tipo_bruxo": "Sangue-Puro"
    }
}

produtos_disponiveis = [
    {"id": 1, "nome": "Varinha Mágica", "preco": 100.00, "categoria": "Feitiçaria", "loja_id": 1, "descricao": "Feita com pena de fênix"},
    {"id": 2, "nome": "Poção de Cura", "preco": 50.00, "categoria": "Poções", "loja_id": 1, "descricao": "Recupera vitalidade"},
    {"id": 3, "nome": "Grimório de Feitiços", "preco": 200.00, "categoria": "Feitiçaria", "loja_id": 1, "descricao": "Feitiços antigos"}
]

carrinho = {}  # carrinho[email] = [produto]
lojas = {
    1: {
        "id": 1,
        "nome": "Loja do Bruxo Mestre",
        "descricao": "Especializada em artigos mágicos raros.",
        "proprietario": "ayme@gmail.com"
    }
}

# Gerador de IDs
proximo_id_produto = 4
proximo_id_loja = 2

def processar_mensagem(mensagem):
    global proximo_id_produto, proximo_id_loja

    acao = mensagem.get('acao')

    if acao == 'login':
        email = mensagem.get('email')
        senha = mensagem.get('senha')
        if email in usuarios and usuarios[email]['senha'] == senha:
            return {'status': 'sucesso'}
        elif email not in usuarios:
            return {'erro': 'usuario_nao_encontrado'}
        else:
            return {'erro': 'senha_incorreta'}

    elif acao == 'cadastro':
        nome = mensagem.get('nome')
        casa = mensagem.get('casa')
        email = mensagem.get('email')
        senha = mensagem.get('senha')
        tipo_bruxo = mensagem.get('tipo_bruxo')
        if email in usuarios:
            return {'erro': 'email_ja_cadastrado'}
        usuarios[email] = {"senha": senha, "nome": nome, "casa": casa, "tipo_bruxo": tipo_bruxo}
        return {'status': 'sucesso'}

    elif acao == 'visualizar_loja':
        categoria = mensagem.get('categoria')
        if categoria:
            produtos_filtrados = [p for p in produtos_disponiveis if p['categoria'].lower() == categoria.lower()]
            return {'status': 'sucesso', 'produtos': produtos_filtrados}
        else:
            return {'status': 'sucesso', 'produtos': produtos_disponiveis}

    elif acao == 'obter_loja':
        id_loja = mensagem.get('id_loja')
        loja = lojas.get(id_loja, None)
        if loja:
            return {'status': 'sucesso', 'loja': loja}
        else:
            return {'erro': 'loja_nao_encontrada'}

    elif acao == 'criar_loja':
        nome = mensagem.get('nome')
        descricao = mensagem.get('descricao')
        proprietario = mensagem.get('email')
        nova_loja = {
            "id": proximo_id_loja,
            "nome": nome,
            "descricao": descricao,
            "proprietario": proprietario
        }
        lojas[proximo_id_loja] = nova_loja
        proximo_id_loja += 1
        return {'status': 'sucesso', 'loja': nova_loja}

    elif acao == 'criar_produto':
        nome = mensagem.get('nome')
        preco = mensagem.get('preco')
        categoria = mensagem.get('categoria')
        descricao = mensagem.get('descricao')
        loja_id = mensagem.get('loja_id')

        novo_produto = {
            "id": proximo_id_produto,
            "nome": nome,
            "preco": preco,
            "categoria": categoria,
            "descricao": descricao,
            "loja_id": loja_id
        }
        produtos_disponiveis.append(novo_produto)
        proximo_id_produto += 1
        return {'status': 'sucesso', 'produto': novo_produto}

    elif acao == 'visualizar_produtos_loja':
        loja_id = mensagem.get('loja_id')
        produtos = [p for p in produtos_disponiveis if p['loja_id'] == loja_id]
        return {'status': 'sucesso', 'produtos': produtos}

    elif acao == 'adicionar_produto_carrinho':
        email = mensagem.get('email')
        produto_id = mensagem.get('produto_id')
        if email not in carrinho:
            carrinho[email] = []
        produto = next((p for p in produtos_disponiveis if p['id'] == produto_id), None)
        if produto:
            carrinho[email].append(produto)
            return {'status': 'sucesso', 'produto_adicionado': produto}
        else:
            return {'erro': 'produto_nao_encontrado'}

    elif acao == 'visualizar_carrinho':
        email = mensagem.get('email')
        return {'status': 'sucesso', 'carrinho': carrinho.get(email, [])}

    elif acao == 'comprar_carrinho':
        email = mensagem.get('email')
        if email not in carrinho or not carrinho[email]:
            return {'erro': 'carrinho_vazio'}
        carrinho[email] = []  # Esvaziar carrinho após compra
        return {'status': 'sucesso', 'mensagem': 'Compra realizada com sucesso'}

    return {'erro': 'acao_invalida'}

def iniciar_servidor(host='localhost', porta=5000):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, porta))
    servidor.listen(5)
    print(f"Servidor mock em execução em {host}:{porta}")

    while True:
        cliente_socket, cliente_endereco = servidor.accept()
        print(f"Conexão recebida de {cliente_endereco}")

        try:
            dados = cliente_socket.recv(4096).decode('utf-8')
            mensagem = json.loads(dados)
            print(f"Mensagem recebida: {mensagem}")
            resposta = processar_mensagem(mensagem)
            cliente_socket.sendall(json.dumps(resposta).encode('utf-8'))
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            cliente_socket.close()

if __name__ == '__main__':
    iniciar_servidor()
