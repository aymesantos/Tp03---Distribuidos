import socket
import json
import os
import base64

# Mock de dados
usuarios = {
    "ayme@gmail.com": {
        "senha": "senha123",
        "nome": "Ayme Faustino",
        "casa": "Grifinória",
        "tipo_bruxo": "Sangue-Puro",
        "foto_perfil": None
    }
}

produtos_disponiveis = [
    {"id": 1, "nome": "Varinha Mágica", "preco": 100.00, "categoria": "Feitiçaria", "loja_id": 1, "descricao": "Feita com pena de fênix"},
    {"id": 2, "nome": "Poção de Cura", "preco": 50.00, "categoria": "Poções", "loja_id": 1, "descricao": "Recupera vitalidade"},
    {"id": 3, "nome": "Grimório de Feitiços", "preco": 200.00, "categoria": "Feitiçaria", "loja_id": 1, "descricao": "Feitiços antigos"}
]


historico_compras = {}  # chave: email do cliente, valor: lista de compras
historico_vendas = {}   # chave: email do vendedor, valor: lista de vendas
carrinho = {}  # carrinho[email] = [produto]
transacoes = []  # Lista de transações realizadas
# Mock de lojas
lojas = {
    1: {
        "id": 1,
        "nome": "Loja do Bruxo Mestre",
        "descricao": "Especializada em artigos mágicos raros.",
        "proprietario": "ayme@gmail.com",
        "produtos": produtos_disponiveis
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
                    # Verificar se o usuário tem uma loja associada
                    tem_loja = False
                    for loja in lojas.values():
                        if loja['proprietario'] == email:
                            tem_loja = True
                            break

                    # Retorna a resposta com a informação de se tem loja ou não
                    return {
                        'status': 'sucesso',
                        'tem_loja': True,
                        'usuario': {
                            'email': email,
                            'nome': usuarios[email]['nome'],
                            'casa': usuarios[email]['casa'],
                            'tipo_bruxo': usuarios[email]['tipo_bruxo'],
                        },
                    }
        
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
            
    elif acao == 'atualizar_foto_perfil':
        email = mensagem.get('email')
        img_base64 = mensagem.get('imagem_base64')

        print(f"Recebendo solicitação de atualizar foto de perfil para o usuário: {email}")

        if not email or not img_base64:
            print("Dados insuficientes para atualizar foto de perfil.")
            return {'status': 'erro', 'erro': 'dados_incompletos'}

        try:
            img_bytes = base64.b64decode(img_base64)

            pasta_perfis = 'fotos_perfil'
            if not os.path.exists(pasta_perfis):
                os.makedirs(pasta_perfis)

            nome_arquivo = os.path.join(pasta_perfis, f"{email.replace('@', '_').replace('.', '_')}.png")

            with open(nome_arquivo, 'wb') as f:
                f.write(img_bytes)

            print(f"Foto de perfil salva em: {nome_arquivo}")

            return {'status': 'sucesso', 'mensagem': 'Foto de perfil atualizada'}

        except Exception as e:
            print(f"Erro ao salvar foto de perfil: {e}")
            return {'status': 'erro', 'erro': 'falha_ao_salvar_imagem'}
        
    elif acao == 'atualizar_perfil':
        email = mensagem.get('email')
        nome = mensagem.get('nome')
        casa_hogwarts = mensagem.get('casa_hogwarts')
        tipo_bruxo = mensagem.get('tipo_bruxo')
        foto_perfil = mensagem.get('foto_perfil')  

        print(f"Recebendo solicitação para atualizar perfil do usuário: {email}")

        if not email or not nome or not casa_hogwarts or not tipo_bruxo:
            print("Dados insuficientes para atualizar perfil.")
            return {'status': 'erro', 'erro': 'dados_incompletos'}

        try:
            if email not in usuarios:
                print(f"Usuário não encontrado: {email}")
                return {'status': 'erro', 'erro': 'usuario_nao_encontrado'}
            
            usuarios[email]['nome'] = nome
            usuarios[email]['casa'] = casa_hogwarts
            usuarios[email]['tipo_bruxo'] = tipo_bruxo
            
            print(f"Dados do usuário atualizados: {email}")
            print(f"Nome: {nome}")
            print(f"Casa de Hogwarts: {casa_hogwarts}")
            print(f"Tipo de Bruxo: {tipo_bruxo}")
            
            if foto_perfil:
                try:
                    img_bytes = base64.b64decode(foto_perfil)
                    
                    pasta_perfis = 'fotos_perfil'
                    if not os.path.exists(pasta_perfis):
                        os.makedirs(pasta_perfis)
                    
                    nome_arquivo = os.path.join(pasta_perfis, f"{email.replace('@', '_').replace('.', '_')}.png")
                    
                    with open(nome_arquivo, 'wb') as f:
                        f.write(img_bytes)
                    
                    usuarios[email]['foto_perfil'] = nome_arquivo
                    
                    print(f"Foto de perfil salva em: {nome_arquivo}")
                    
                except Exception as e:
                    print(f"Erro ao salvar foto de perfil: {e}")
            
            return {'status': 'sucesso', 'mensagem': 'Perfil atualizado com sucesso', 'dados': {
                'nome': nome,
                'casa': casa_hogwarts,
                'tipo_bruxo': tipo_bruxo,
                'foto_perfil': usuarios[email]['foto_perfil']
            }}
                
        except Exception as e:
            print(f"Erro ao atualizar perfil: {e}")
            return {'status': 'erro', 'erro': 'falha_ao_atualizar_perfil'}


    elif acao == 'obter_perfil':
        email = mensagem.get('email')
        
        if not email:
            return {'status': 'erro', 'erro': 'email_nao_fornecido'}
        
        if email not in usuarios:
            return {'status': 'erro', 'erro': 'usuario_nao_encontrado'}

        dados_perfil = {
            'nome': usuarios[email].get('nome', ''),
            'casa': usuarios[email].get('casa', ''),
            'tipo_bruxo': usuarios[email].get('tipo_bruxo', '')
        }

        if 'foto_perfil' in usuarios[email]:
            dados_perfil['foto_perfil'] = usuarios[email]['foto_perfil']
        
        print(f"Enviando dados do perfil para o usuário: {email}")
        
        return {
            'status': 'sucesso',
            'dados_perfil': dados_perfil
        }

    elif acao == 'obter_loja':
        email = mensagem.get('email')
        print(f"Recebendo solicitação de obter loja com email: {email}")
        
        loja = None
        for loja_data in lojas.values():
            if loja_data['proprietario'] == email:
                loja = loja_data
                break
        
        if loja:
            print(f"Loja encontrada: {loja}")
            return {
                'status': 'sucesso',
                'nome_loja': loja.get('nome'),
                'descricao': loja.get('descricao'),
                'produtos': loja.get('produtos', [])
            }
        else:
            print("Loja não encontrada.")
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
        imagem_base64 = mensagem.get('imagem_base64')

        novo_produto = {
            "id": proximo_id_produto,
            "nome": nome,
            "preco": preco,
            "categoria": categoria,
            "descricao": descricao,
            "loja_id": loja_id,
            "imagem_base64": imagem_base64  # só uma imagem
        }
        produtos_disponiveis.append(novo_produto)
        proximo_id_produto += 1
        return {'status': 'sucesso', 'produto': novo_produto}

    elif acao == 'editar_produto':
        produto_id = mensagem.get('produto_id')
        nome = mensagem.get('nome')
        preco = mensagem.get('preco')
        categoria = mensagem.get('categoria')
        descricao = mensagem.get('descricao')
        imagem_base64 = mensagem.get('imagem_base64')

        produto = next((p for p in produtos_disponiveis if p['id'] == produto_id), None)
        if produto:
            produto['nome'] = nome
            produto['preco'] = preco
            produto['categoria'] = categoria
            produto['descricao'] = descricao
            if imagem_base64 is not None:
                produto['imagem_base64'] = imagem_base64
            return {'status': 'sucesso', 'produto_editado': produto}
        else:
            return {'erro': 'produto_nao_encontrado'}

    
    elif acao == 'listar_meus_produtos':
        email = mensagem.get('email')
        print(f"Solicitação para listar produtos da loja do usuário: {email}")

        # Buscar a loja correspondente ao email
        loja_encontrada = None
        for loja in lojas.values():
            if loja['proprietario'] == email:
                loja_encontrada = loja
                break

        if loja_encontrada:
            return {
                'status': 'sucesso',
                'produtos': loja_encontrada.get('produtos', [])
            }
        else:
            return {
                'status': 'erro',
                'mensagem': 'Loja não encontrada para este email.'
            }

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

    elif acao == 'finalizar_compra':
        email = mensagem.get('email')
        metodo_pagamento = 'galeao'  
        if not email or email not in carrinho or not carrinho[email]:
            return {'erro': 'carrinho_vazio'}

        itens = carrinho[email]
        carrinho[email] = [] 
        compra = {
            'produtos': itens,
            'metodo_pagamento': metodo_pagamento
        }
        historico_compras.setdefault(email, []).append(compra)
        for item in itens:
            vendedor = item.get('vendedor')
            if vendedor:
                venda = {
                    'produto': item,
                    'comprador': email,
                    'metodo_pagamento': metodo_pagamento
                }
                historico_vendas.setdefault(vendedor, []).append(venda)

        return {'status': 'sucesso', 'mensagem': 'Compra realizada com sucesso'}

    
    elif acao == 'listar_produtos':
        filtros = mensagem.get('filtros', {})
        categoria = filtros.get('categoria')
        termo_busca = filtros.get('termo_busca')

        print(f"[SERVIDOR] Listando produtos - Categoria: {categoria}, Termo de busca: {termo_busca}")
        print(f"[SERVIDOR] Produtos disponíveis: {len(produtos_disponiveis)}")

        produtos_filtrados = produtos_disponiveis.copy()

        if categoria:
            produtos_filtrados = [p for p in produtos_filtrados if p.get('categoria', '').lower() == categoria.lower()]
            print(f"[SERVIDOR] Após filtro por categoria ({categoria}): {len(produtos_filtrados)} produtos")
            
        if termo_busca:
            termo = termo_busca.lower()
            produtos_filtrados = [
                p for p in produtos_filtrados
                if termo in p.get('nome', '').lower() or termo in p.get('descricao', '').lower()
                
            ]
            print(f"[SERVIDOR] Após filtro por termo de busca ({termo}): {len(produtos_filtrados)} produtos")
        return {'status': 'sucesso', 'produtos': produtos_filtrados}

    
    elif acao == 'historico_compras':
        email = mensagem.get('email')

        compras_usuario = []
        for transacao in transacoes:
            if transacao.get('comprador_email') == email:
                compras_usuario.append({
                    'produto': transacao['produto'],
                    'quantidade': transacao['quantidade'],
                    'total': transacao['total'],
                    'data': transacao['data']
                })
        
        return {'status': 'sucesso', 'compras': compras_usuario}

    elif acao == 'historico_vendas':
        email = mensagem.get('email')

        vendas_usuario = []
        for transacao in transacoes:
            if transacao.get('vendedor_email') == email:
                vendas_usuario.append({
                    'produto': transacao['produto'],
                    'quantidade': transacao['quantidade'],
                    'total': transacao['total'],
                    'data': transacao['data']
                })
        
        return {'status': 'sucesso', 'vendas': vendas_usuario}



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
            while True:
                dados = cliente_socket.recv(4096)
                if not dados:
                    break
                mensagem = json.loads(dados.decode('utf-8'))
                print(f"Mensagem recebida: {mensagem}")
                resposta = processar_mensagem(mensagem)
                cliente_socket.sendall(json.dumps(resposta).encode('utf-8'))
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            cliente_socket.close()

if __name__ == '__main__':
    iniciar_servidor()
