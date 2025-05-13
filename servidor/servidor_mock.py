import socket
import json
import threading

# Dados do servidor
host = 'localhost'
porta = 5000

# Mock de dados
usuarios = {
    "ayme@gmail.com": {
        "senha": "senha123",
        "nome": "Ayme Faustino",
        "casa": "Grifinória",
        "tipo_bruxo": "Sangue-Puro"
    },
    
    "pedro@gmail.com": {
        "senha": "senha456",
        "nome": "Pedro Augusto",
        "casa": "Sonserina",
        "tipo_bruxo": "Sangue-Puro"
    }
    
}

produtos_disponiveis = [
    {"id": 1, "nome": "Varinha Mágica", "preco": 100.00, "categoria": "Feitiçaria", "loja_id": 1, "descricao": "Feita com pena de fênix"},
    {"id": 2, "nome": "Poção de Cura", "preco": 50.00, "categoria": "Poções", "loja_id": 1, "descricao": "Recupera vitalidade"},
    {"id": 3, "nome": "Grimório de Feitiços", "preco": 200.00, "categoria": "Feitiçaria", "loja_id": 1, "descricao": "Feitiços antigos"},
    {"id": 4, "nome": "Capa da Invisibilidade", "preco": 500.00, "categoria": "Artefatos", "loja_id": 1, "descricao": "Torna o usuário invisível"},
    {"id": 5, "nome": "Vassoura Nimbus 2000", "preco": 300.00, "categoria": "Transporte", "loja_id": 1, "descricao": "Vassoura de alta velocidade para quadribol"},
    {"id": 6, "nome": "Mapa do Maroto", "preco": 150.00, "categoria": "Artefatos", "loja_id": 1, "descricao": "Mostra a localização de todos em Hogwarts"},
    {"id": 7, "nome": "Chapéu Seletor", "preco": 250.00, "categoria": "Artefatos", "loja_id": 1, "descricao": "Determina a casa de Hogwarts do usuário"},
    {"id": 8, "nome": "Poção Polissuco", "preco": 120.00, "categoria": "Poções", "loja_id": 1, "descricao": "Permite assumir a aparência de outra pessoa"},
    {"id": 9, "nome": "Ovo de Dragão", "preco": 1000.00, "categoria": "Criaturas Mágicas", "loja_id": 1, "descricao": "Raro e altamente valioso"},
    {"id": 10, "nome": "Relógio de Areia do Tempo", "preco": 800.00, "categoria": "Artefatos", "loja_id": 1, "descricao": "Permite voltar no tempo por curtos períodos"},
    {"id": 11, "nome": "Livro Monstruoso dos Monstros", "preco": 75.00, "categoria": "Livros", "loja_id": 1, "descricao": "Livro que precisa ser domado para ser lido"},
    {"id": 12, "nome": "Espelho de Ojesed", "preco": 400.00, "categoria": "Artefatos", "loja_id": 1, "descricao": "Mostra o desejo mais profundo do coração"},
    {"id": 13, "nome": "Ferroada de Weasley", "preco": 30.00, "categoria": "Brincadeiras", "loja_id": 1, "descricao": "Brinquedo mágico da loja dos Weasley"}
]

# Dicionário de produtos de cada usuário
carrinho = {}

lojas = {
    1: {
        "id": 1,
        "nome": "Loja do Bruxo Mestre",
        "descricao": "Especializada em artigos mágicos raros.",
        "proprietario": "ayme@gmail.com"
    },
    
    2: {
        "id": 2,
        "nome": "Empório das Poções",
        "descricao": "Focado em poções e ingredientes mágicos.",
        "proprietario": "pedro@gmail.com"
    }
}

# Dicionário de histórico de transações
historico_transacoes = {}

# Gerador de IDs
proximo_id_produto = 4
proximo_id_loja = 2


# SERVIDOR
# Função que lida com cada cliente
def handle_client(cliente_socket, cliente_endereco):
    try:
        mensagem = cliente_socket.recv(1024).decode('utf-8')
        if not mensagem:
            return
        
        mensagem = json.loads(mensagem)
        print(f"Mensagem recebida de {cliente_endereco}: {mensagem}")
        
        resposta = processar_mensagem(mensagem)
        resposta_json = json.dumps(resposta)
        cliente_socket.sendall(resposta_json.encode('utf-8'))

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        resposta_erro = {'erro': 'erro_interno'}
        cliente_socket.sendall(json.dumps(resposta_erro).encode('utf-8'))

    finally:
        cliente_socket.close()

# Iniciar o servidor
def iniciar_servidor(host = host, porta = porta):
    # Criação do socket
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, porta))
    servidor.listen(10)
    
    print(f"Servidor mock em execução em {host}:{porta}")
    
    while True:
        # Aceitar conexões de clientes
        cliente_socket, cliente_endereco = servidor.accept()
        cliente_thread = threading.Thread(target=handle_client, args=(cliente_socket, cliente_endereco))
        cliente_thread.start()
        
        print(f"Conexão recebida de {cliente_endereco}")

# CLIENTE
# Função de login
def realizar_login(email, senha):
    if email in usuarios:
        if usuarios[email]['senha'] == senha:
            return {'status': 'sucesso'}
        else:
            return {'erro': 'senha_incorreta'}
    else:
        return {'erro': 'usuario_nao_encontrado'}

# Função de cadastro
def realizar_cadastro(nome, casa, email, senha, tipo_bruxo):
    if email in usuarios:
        return {'erro': 'email_ja_cadastrado'}
    
    usuarios[email] = {"senha": senha, "nome": nome, "casa": casa, "tipo_bruxo": tipo_bruxo}
    return {'status': 'sucesso'}

# Função de adicionar produto ao carrinho
def adicionar_produto_carrinho(email, produto_id):
    if email not in carrinho:
        carrinho[email] = []
    
    produto = next((p for p in produtos_disponiveis if p['id'] == produto_id), None)
    if produto:
        carrinho[email].append(produto)
        return {'status': 'sucesso', 'produto_adicionado': produto}
    else:
        return {'erro': 'produto_nao_encontrado'}

# Função de visualizar carrinho
def visualizar_carrinho(email):
    if email in carrinho:
        return {'status': 'sucesso', 'carrinho': carrinho[email]}
    else:
        return {'erro': 'carrinho_vazio'}

# Função de visualizar loja
def visualizar_loja():
    return {'status': 'sucesso', 'produtos': produtos_disponiveis}

# Função para remover produto do carrinho
def remover_produto_carrinho(email, produto_id):
    if email not in carrinho or not carrinho[email]:
        return {'erro': 'carrinho_vazio'}
    
    produto = next((p for p in carrinho[email] if p['id'] == produto_id), None)
    if produto:
        carrinho[email].remove(produto)
        return {'status': 'produto_removido', 'produto': produto}
    else:
        return {'erro': 'produto_nao_encontrado'}
    
# Validar a quantidade de produtos no estoque
def validar_estoque(produto_id, quantidade):
    produto = next((p for p in produtos_disponiveis if p['id'] == produto_id), None)
    if produto and quantidade <= 10:  # Supondo que o estoque tenha 10 unidades
        return True
    return False

# Função de finalizar a compra com validação de estoque
def finalizar_compra(email, metodo_pagamento, produto_id, quantidade):
    if email not in carrinho or not carrinho[email]:
        return {'erro': 'carrinho_vazio'}
    
    if not validar_estoque(produto_id, quantidade):
        return {'erro': 'estoque_insuficiente'}
    
    if metodo_pagamento not in ['cartao', 'boleto', 'pix']:
        return {'erro': 'metodo_pagamento_invalido'}
    
    # Simula o pagamento sendo aprovado
    carrinho[email] = []  # Limpa o carrinho após a compra
    return {'status': 'compra_finalizada', 'metodo_pagamento': metodo_pagamento}

# Função para buscar produtos por categoria
def buscar_produtos_por_categoria(categoria):
    produtos_filtrados = [p for p in produtos_disponiveis if p['categoria'].lower() == categoria.lower()]
    if produtos_filtrados:
        return {'status': 'sucesso', 'produtos': produtos_filtrados}
    else:
        return {'erro': 'categoria_nao_encontrada'}

# Função para avaliar um produto
def avaliar_produto(email, produto_id, avaliacao, comentario):
    produto = next((p for p in produtos_disponiveis if p['id'] == produto_id), None)
    if produto:
        if 'avaliacoes' not in produto:
            produto['avaliacoes'] = []
        produto['avaliacoes'].append({'usuario': email, 'avaliacao': avaliacao, 'comentario': comentario})
        return {'status': 'avaliacao_adicionada'}
    else:
        return {'erro': 'produto_nao_encontrado'}

# Função para visualizar avaliações de um produto
def visualizar_avaliacoes(produto_id):
    produto = next((p for p in produtos_disponiveis if p['id'] == produto_id), None)
    if produto and 'avaliacoes' in produto:
        return {'status': 'sucesso', 'avaliacoes': produto['avaliacoes']}
    elif produto:
        return {'status': 'sucesso', 'avaliacoes': []}
    else:
        return {'erro': 'produto_nao_encontrado'}

# Função para recomendar produtos com base em categoria
def recomendar_produtos(categoria):
    produtos_recomendados = [p for p in produtos_disponiveis if p['categoria'].lower() == categoria.lower()][:5]
    return {'status': 'sucesso', 'recomendacoes': produtos_recomendados}

# VENDEDOR
# Função de criar uma loja
def criar_loja(email, nome_loja, descricao, categoria):
    if email in lojas:
        return {'erro': 'loja_ja_existe'}
    
    lojas[email] = {'nome': nome_loja, 'descricao': descricao, 'categoria': categoria, 'produtos': []}
    return {'status': 'loja_criada'}

# Função de adicionar produto na loja
def adicionar_produto_loja(email, nome_produto, descricao_produto, preco_produto):
    if email not in lojas:
        return {'erro': 'loja_nao_encontrada'}
    
    produto = {'nome': nome_produto, 'descricao': descricao_produto, 'preco': preco_produto}
    lojas[email]['produtos'].append(produto)
    return {'status': 'produto_adicionado'}

# Função de editar loja
def editar_loja(email, nome_loja=None, descricao=None, categoria=None):
    if email not in lojas:
        return {'erro': 'loja_nao_encontrada'}
    
    if nome_loja:
        lojas[email]['nome'] = nome_loja
    if descricao:
        lojas[email]['descricao'] = descricao
    if categoria:
        lojas[email]['categoria'] = categoria

    return {'status': 'loja_atualizada'}

# Função de pausar ou ativar um anúncio
def pausar_ativar_produto(email, produto_id, status):
    if email not in lojas:
        return {'erro': 'loja_nao_encontrada'}

    produto = next((p for p in lojas[email]['produtos'] if p['id'] == produto_id), None)
    if produto:
        produto['status'] = status
        return {'status': f'produto_{status}'}
    else:
        return {'erro': 'produto_nao_encontrado'}

# Função de registrar transação
def registrar_transacao(email, transacao):
    if email not in historico_transacoes:
        historico_transacoes[email] = []
    
    historico_transacoes[email].append(transacao)

# Função de visualizar o histórico de transações
def visualizar_historico(email):
    if email not in historico_transacoes:
        return {'erro': 'historico_nao_encontrado'}
    
    return {'status': 'sucesso', 'historico': historico_transacoes[email]}

# Função de gerenciar avaliações de produtos
def gerenciar_avaliacoes(email, produto_id, avaliacao, comentario):
    if email not in lojas:
        return {'erro': 'loja_nao_encontrada'}
    
    produto = next((p for p in lojas[email]['produtos'] if p['id'] == produto_id), None)
    if produto:
        if 'avaliacoes' not in produto:
            produto['avaliacoes'] = []
        produto['avaliacoes'].append({'avaliacao': avaliacao, 'comentario': comentario})
        return {'status': 'avaliacao_adicionada'}
    else:
        return {'erro': 'produto_nao_encontrado'}

# Função de gerar relatório de vendas
def gerar_relatorio_vendas(email):
    if email not in historico_transacoes:
        return {'erro': 'historico_nao_encontrado'}
    
    total_vendas = len(historico_transacoes[email])
    receita_total = sum(transacao['valor'] for transacao in historico_transacoes[email])
    return {'status': 'sucesso', 'total_vendas': total_vendas, 'receita_total': receita_total}

# Função de configurar promoções
def configurar_promocao(email, produto_id, desconto):
    if email not in lojas:
        return {'erro': 'loja_nao_encontrada'}
    
    produto = next((p for p in lojas[email]['produtos'] if p['id'] == produto_id), None)
    if produto:
        produto['preco_promocional'] = produto['preco'] * (1 - desconto / 100)
        return {'status': 'promocao_configurada', 'preco_promocional': produto['preco_promocional']}
    else:
        return {'erro': 'produto_nao_encontrado'}


# PROCESSO DE MENSAGENS
# Função principal de processamento de mensagens
def processar_mensagem(mensagem):
    acao = mensagem.get('acao')

    # Ação de login
    if acao == 'login':
        email = mensagem.get('email')
        senha = mensagem.get('senha')
        return realizar_login(email, senha)
    
    # Ação de cadastro
    elif acao == 'cadastro':
        nome = mensagem.get('nome')
        casa = mensagem.get('casa')
        email = mensagem.get('email')
        senha = mensagem.get('senha')
        tipo_bruxo = mensagem.get('tipo_bruxo')
        return realizar_cadastro(nome, casa, email, senha, tipo_bruxo)
    
    # Ações para clientes
    elif acao == 'adicionar_produto_carrinho':
        email = mensagem.get('email')
        produto_id = mensagem.get('produto_id')
        return adicionar_produto_carrinho(email, produto_id)
    
    elif acao == 'visualizar_carrinho':
        email = mensagem.get('email')
        return visualizar_carrinho(email)
    
    # Ações para vendedores
    elif acao == 'criar_loja':
        email = mensagem.get('email')
        nome_loja = mensagem.get('nome_loja')
        descricao = mensagem.get('descricao')
        categoria = mensagem.get('categoria')
        return criar_loja(email, nome_loja, descricao, categoria)
    
    elif acao == 'adicionar_produto_loja':
        email = mensagem.get('email')
        nome_produto = mensagem.get('nome_produto')
        descricao_produto = mensagem.get('descricao_produto')
        preco_produto = mensagem.get('preco_produto')
        return adicionar_produto_loja(email, nome_produto, descricao_produto, preco_produto)

    return {'erro': 'acao_invalida'}


if __name__ == '__main__':
    iniciar_servidor()
