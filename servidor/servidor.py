import socket
import json
import os
import threading

# Função utilitária para comunicação com o servidor de dados
DADOS_HOST = 'localhost'
DADOS_PORTA = 5003

def requisitar_dados(operacao, parametros):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            try:
                s.connect((DADOS_HOST, DADOS_PORTA))
            except Exception as e:
                print(f"[ERRO] Falha ao conectar ao servidor de dados: {e}")
                return {'status': 'erro', 'mensagem': f'Falha ao conectar ao servidor de dados: {e}'}
            mensagem = json.dumps({"operacao": operacao, "parametros": parametros})
            try:
                s.sendall(mensagem.encode())
            except Exception as e:
                print(f"[ERRO] Falha ao enviar dados para o servidor de dados: {e}")
                return {'status': 'erro', 'mensagem': f'Falha ao enviar dados para o servidor de dados: {e}'}
            try:
                resposta = s.recv(4096)
                if not resposta:
                    print("[ERRO] Resposta vazia do servidor de dados")
                    return {'status': 'erro', 'mensagem': 'Resposta vazia do servidor de dados'}
                return json.loads(resposta.decode())
            except Exception as e:
                print(f"[ERRO] Falha ao receber resposta do servidor de dados: {e}")
                return {'status': 'erro', 'mensagem': f'Falha ao receber resposta do servidor de dados: {e}'}
    except Exception as e:
        print(f"[ERRO] Erro inesperado na comunicação com servidor de dados: {e}")
        return {'status': 'erro', 'mensagem': f'Erro inesperado na comunicação com servidor de dados: {e}'}

def processar_mensagem(mensagem):
    acao = mensagem.get('acao')

    if acao == 'login':
        email = mensagem.get('email')
        senha = mensagem.get('senha')
        resposta = requisitar_dados('autenticar_usuario', {'email': email, 'senha': senha})
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao autenticar usuário') if resposta else 'Erro ao autenticar usuário'}
        usuario = resposta['usuario']
        # Verifica se o usuário tem loja
        resposta_loja = requisitar_dados('listar_lojas', {})
        tem_loja = False
        if resposta_loja.get('status') == 'ok':
            for loja in resposta_loja['lojas']:
                if loja['usuario_id'] == usuario['id']:
                    tem_loja = True
                    break
        return {
            'status': 'sucesso',
            'tem_loja': tem_loja,
            'usuario': {
                'email': usuario['email'],
                'nome': usuario['nome'],
                'casa': usuario.get('casa'),
                'tipo_bruxo': usuario.get('tipo')
            }
        }

    elif acao == 'cadastro':
        nome = mensagem.get('nome')
        casa = mensagem.get('casa')
        email = mensagem.get('email')
        senha = mensagem.get('senha')
        tipo_bruxo = mensagem.get('tipo')
        resposta = requisitar_dados('cadastrar_usuario', {
            'nome': nome,
            'email': email,
            'senha': senha,
            'tipo': tipo_bruxo,
            'casa': casa
        })
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao cadastrar usuário') if resposta else 'Erro ao cadastrar usuário'}
        if resposta.get('status') == 'ok':
            return {'status': 'sucesso'}
        elif resposta.get('mensagem', '').startswith('UNIQUE constraint failed: usuarios.email'):
            return {'erro': 'email_ja_cadastrado'}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}

    elif acao == 'visualizar_loja':
        categoria = mensagem.get('categoria')
        resposta = requisitar_dados('listar_produtos', {})
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao listar produtos') if resposta else 'Erro ao listar produtos'}
        produtos = resposta.get('dados', [])
        if categoria:
            produtos_filtrados = [p for p in produtos if p.get('categoria', '').lower() == categoria.lower()]
            return {'status': 'sucesso', 'produtos': produtos_filtrados}
        else:
            return {'status': 'sucesso', 'produtos': produtos}

    elif acao == 'obter_perfil':
        email = mensagem.get('email')
        # Buscar usuário pelo e-mail no backend de dados
        resposta_usuario = requisitar_dados('buscar_usuario', {'email': email})
        if not resposta_usuario or resposta_usuario.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_usuario.get('mensagem', 'Erro ao buscar usuário') if resposta_usuario else 'Erro ao buscar usuário'}
        usuario = resposta_usuario.get('usuario')
        dados_perfil = {
            'nome': usuario.get('nome', ''),
            'casa_hogwarts': usuario.get('casa', ''),
            'tipo_bruxo': usuario.get('tipo', '')
        }
        return {
            'status': 'sucesso',
            'dados_perfil': dados_perfil
        }

    elif acao == 'obter_loja':
        email = mensagem.get('email')
        # Buscar usuário pelo e-mail
        resposta_usuario = requisitar_dados('buscar_usuario', {'email': email})
        if not resposta_usuario or resposta_usuario.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_usuario.get('mensagem', 'Erro ao buscar usuário') if resposta_usuario else 'Erro ao buscar usuário'}
        usuario = resposta_usuario.get('usuario')
        usuario_id = usuario['id']
        resposta_lojas = requisitar_dados('listar_lojas', {})
        if not resposta_lojas or resposta_lojas.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_lojas.get('mensagem', 'Erro ao listar lojas') if resposta_lojas else 'Erro ao listar lojas'}
        loja = next((l for l in resposta_lojas.get('lojas', []) if l['usuario_id'] == usuario_id), None)
        if loja:
            resposta_produtos = requisitar_dados('listar_produtos', {})
            if not resposta_produtos or resposta_produtos.get('status') == 'erro':
                return {'status': 'erro', 'mensagem': resposta_produtos.get('mensagem', 'Erro ao listar produtos da loja') if resposta_produtos else 'Erro ao listar produtos da loja'}
            produtos = [p for p in resposta_produtos.get('dados', []) if p['loja_id'] == loja['id']]
            return {
                'status': 'sucesso',
                'id': loja.get('id'),
                'nome_loja': loja.get('nome'),
                'descricao': loja.get('descricao'),
                'produtos': produtos
            }
        else:
            return {'erro': 'loja_nao_encontrada'}

    elif acao == 'criar_loja':
        nome = mensagem.get('nome') or mensagem.get('nome_loja')
        descricao = mensagem.get('descricao')
        proprietario = mensagem.get('email')
        resposta_usuario = requisitar_dados('buscar_usuario', {'email': proprietario})
        if not resposta_usuario or resposta_usuario.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_usuario.get('mensagem', 'Erro ao buscar usuário') if resposta_usuario else 'Erro ao buscar usuário'}
        usuario_id = resposta_usuario['usuario']['id']
        resposta = requisitar_dados('cadastrar_loja', {
            'nome': nome,
            'descricao': descricao,
            'usuario_id': usuario_id
        })
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao cadastrar loja') if resposta else 'Erro ao cadastrar loja'}
        if resposta.get('status') == 'ok':
            return {'status': 'sucesso', 'loja': resposta.get('loja', {})}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}

    elif acao == 'criar_produto':
        nome = mensagem.get('nome')
        preco = mensagem.get('preco')
        categoria = mensagem.get('categoria')
        descricao = mensagem.get('descricao')
        loja_id = mensagem.get('loja_id')
        estoque = mensagem.get('estoque', 1)
        resposta = requisitar_dados('cadastrar_produto', {
            'nome': nome,
            'descricao': descricao,
            'preco': preco,
            'estoque': estoque,
            'loja_id': loja_id,
            'categoria': categoria
        })
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao cadastrar produto') if resposta else 'Erro ao cadastrar produto'}
        if resposta.get('status') == 'ok':
            return {'status': 'sucesso', 'produto': resposta}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}

    elif acao == 'editar_produto':
        produto_id = mensagem.get('produto_id')
        nome = mensagem.get('nome')
        preco = mensagem.get('preco')
        categoria = mensagem.get('categoria')
        descricao = mensagem.get('descricao')
        estoque = mensagem.get('estoque', 1)
        resposta = requisitar_dados('editar_produto', {
            'id': produto_id,
            'nome': nome,
            'descricao': descricao,
            'preco': preco,
            'estoque': estoque
        })
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao editar produto') if resposta else 'Erro ao editar produto'}
        if resposta.get('status') == 'ok':
            return {'status': 'sucesso'}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}

    
    elif acao == 'listar_meus_produtos':
        email = mensagem.get('email')
        resposta_usuario = requisitar_dados('buscar_usuario', {'email': email})
        if not resposta_usuario or resposta_usuario.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_usuario.get('mensagem', 'Erro ao buscar usuário') if resposta_usuario else 'Erro ao buscar usuário'}
        usuario_id = resposta_usuario['usuario']['id']
        resposta_lojas = requisitar_dados('listar_lojas', {})
        if not resposta_lojas or resposta_lojas.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_lojas.get('mensagem', 'Erro ao listar lojas') if resposta_lojas else 'Erro ao listar lojas'}
        lojas_usuario = [l for l in resposta_lojas.get('lojas', []) if l['usuario_id'] == usuario_id]
        produtos = []
        for loja in lojas_usuario:
            resposta_produtos = requisitar_dados('listar_produtos', {})
            if not resposta_produtos or resposta_produtos.get('status') == 'erro':
                return {'status': 'erro', 'mensagem': resposta_produtos.get('mensagem', 'Erro ao listar produtos da loja') if resposta_produtos else 'Erro ao listar produtos da loja'}
            produtos += [p for p in resposta_produtos.get('dados', []) if p['loja_id'] == loja['id']]
        return {'status': 'sucesso', 'produtos': produtos}

    elif acao == 'visualizar_produtos_loja':
        loja_id = mensagem.get('loja_id')
        resposta = requisitar_dados('listar_produtos', {})
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao listar produtos da loja') if resposta else 'Erro ao listar produtos da loja'}
        produtos = [p for p in resposta.get('dados', []) if p['loja_id'] == loja_id]
        return {'status': 'sucesso', 'produtos': produtos}
    

    elif acao == 'adicionar_produto_carrinho':
        email = mensagem.get('email')
        produto_id = mensagem.get('produto_id')
        quantidade = mensagem.get('quantidade', 1)
        resposta = requisitar_dados('adicionar_produto_carrinho', {
            'email': email,
            'produto_id': produto_id,
            'quantidade': quantidade
        })
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao adicionar produto ao carrinho') if resposta else 'Erro ao adicionar produto ao carrinho'}
        if resposta.get('status') == 'ok':
            return {'status': 'sucesso'}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}


    elif acao == 'visualizar_carrinho':
        email = mensagem.get('email')
        resposta = requisitar_dados('visualizar_carrinho', {'email': email})
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao visualizar carrinho') if resposta else 'Erro ao visualizar carrinho'}
        if resposta.get('status') == 'ok':
            return {'status': 'sucesso', 'carrinho': resposta.get('carrinho', [])}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}


    elif acao == 'finalizar_compra':
        email = mensagem.get('email')
        metodo_pagamento = 'galeao'
        resposta_usuario = requisitar_dados('buscar_usuario', {'email': email})
        if not resposta_usuario or resposta_usuario.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_usuario.get('mensagem', 'Erro ao buscar usuário') if resposta_usuario else 'Erro ao buscar usuário'}
        usuario_id = resposta_usuario['usuario']['id']
        resposta_carrinho = requisitar_dados('visualizar_carrinho', {'email': email})
        if not resposta_carrinho or resposta_carrinho.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_carrinho.get('mensagem', 'Erro ao buscar carrinho') if resposta_carrinho else 'Erro ao buscar carrinho'}
        itens = resposta_carrinho.get('carrinho', [])
        if not itens:
            return {'erro': 'carrinho_vazio'}
        # Buscar preços dos produtos
        resposta_produtos = requisitar_dados('listar_produtos', {})
        if not resposta_produtos or resposta_produtos.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_produtos.get('mensagem', 'Erro ao buscar produtos') if resposta_produtos else 'Erro ao buscar produtos'}
        produtos = resposta_produtos.get('dados', [])
        produtos_dict = {p['id']: p for p in produtos}
        itens_completos = []
        for item in itens:
            produto_id = item['produto_id']
            quantidade = item['quantidade']
            preco_unitario = produtos_dict.get(produto_id, {}).get('preco', 0)
            itens_completos.append({
                'produto_id': produto_id,
                'quantidade': quantidade,
                'preco_unitario': preco_unitario
            })
        resposta = requisitar_dados('comprar_produto', {
            'cliente_id': usuario_id,
            'itens': itens_completos
        })
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao finalizar compra') if resposta else 'Erro ao finalizar compra'}
        if resposta.get('status') == 'ok':
            # Esvaziar o carrinho do usuário após a compra
            requisitar_dados('remover_produto_carrinho', {'email': email, 'produto_id': None})
            return {'status': 'sucesso', 'mensagem': 'Compra realizada com sucesso'}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}

    
    elif acao == 'listar_produtos':
        filtros = mensagem.get('filtros', {})
        resposta = requisitar_dados('listar_produtos', {})
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao listar produtos') if resposta else 'Erro ao listar produtos'}
        produtos = resposta.get('dados', [])
        categoria = filtros.get('categoria')
        termo_busca = filtros.get('termo_busca')
        produtos_filtrados = produtos
        if categoria:
            produtos_filtrados = [p for p in produtos_filtrados if p.get('categoria', '').lower() == categoria.lower()]
        if termo_busca:
            termo = termo_busca.lower()
            produtos_filtrados = [
                p for p in produtos_filtrados
                if termo in p.get('nome', '').lower() or termo in p.get('descricao', '').lower()
            ]
        return {'status': 'sucesso', 'produtos': produtos_filtrados}

    
    elif acao == 'historico_compras':
        email = mensagem.get('email')
        resposta_usuario = requisitar_dados('buscar_usuario', {'email': email})
        if not resposta_usuario or resposta_usuario.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_usuario.get('mensagem', 'Erro ao buscar usuário') if resposta_usuario else 'Erro ao buscar usuário'}
        usuario_id = resposta_usuario['usuario']['id']
        resposta = requisitar_dados('listar_compras_cliente', {'cliente_id': usuario_id})
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao buscar histórico de compras') if resposta else 'Erro ao buscar histórico de compras'}
        if resposta.get('status') == 'ok':
            return {'status': 'sucesso', 'compras': resposta.get('compras', [])}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}

    elif acao == 'historico_vendas':
        email = mensagem.get('email')
        resposta_usuario = requisitar_dados('buscar_usuario', {'email': email})
        if not resposta_usuario or resposta_usuario.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta_usuario.get('mensagem', 'Erro ao buscar usuário') if resposta_usuario else 'Erro ao buscar usuário'}
        usuario_id = resposta_usuario['usuario']['id']
        resposta = requisitar_dados('listar_vendas_vendedor', {'usuario_id': usuario_id})
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao buscar histórico de vendas') if resposta else 'Erro ao buscar histórico de vendas'}
        if resposta.get('status') == 'ok':
            return {'status': 'sucesso', 'vendas': resposta.get('vendas', [])}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}

    elif acao == 'remover_produto_carrinho':
        email = mensagem.get('email')
        produto_id = mensagem.get('produto_id')
        resposta = requisitar_dados('remover_produto_carrinho', {
            'email': email,
            'produto_id': produto_id
        })
        if not resposta or resposta.get('status') == 'erro':
            return {'status': 'erro', 'mensagem': resposta.get('mensagem', 'Erro ao remover produto do carrinho') if resposta else 'Erro ao remover produto do carrinho'}
        if resposta.get('status') == 'ok':
            return {'status': 'sucesso'}
        else:
            return {'erro': resposta.get('mensagem', 'erro_desconhecido')}

    return {'erro': 'acao_invalida'}

def atender_cliente(cliente_socket, cliente_endereco):
    print(f"[NOVA CONEXÃO] {cliente_endereco} conectado.")
    try:
        while True:
            dados = cliente_socket.recv(4096)
            if not dados:
                break
            mensagem = json.loads(dados.decode('utf-8'))
            print(f"[MENSAGEM RECEBIDA DE {cliente_endereco}] {mensagem}")
            resposta = processar_mensagem(mensagem)
            cliente_socket.sendall(json.dumps(resposta).encode('utf-8'))
    except Exception as e:
        print(f"[ERRO] Cliente {cliente_endereco}: {e}")
    finally:
        print(f"[DESCONECTADO] {cliente_endereco}")
        cliente_socket.close()

def iniciar_servidor(host='localhost', porta=5000):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, porta))
    servidor.listen(5)
    print(f"[SERVIDOR ONLINE] Aguardando conexões em {host}:{porta}")

    while True:
        cliente_socket, cliente_endereco = servidor.accept()
        thread = threading.Thread(target=atender_cliente, args=(cliente_socket, cliente_endereco))
        thread.start()
        print(f"[ATIVO] Conexões ativas: {threading.active_count() - 1}")  # -1 para descontar a thread principal

if __name__ == '__main__':
    iniciar_servidor()