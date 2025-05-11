import socket
import json

# Dados simulados de produtos e usuários
usuarios = {
    "teste@exemplo.com": {"senha": "senha123", "nome": "Test User", "casa": "Grifinória", "tipo_bruxo": "Bruxo"}
}

produtos_disponiveis = [
    {"id": 1, "nome": "Varinha Mágica", "preco": 100.00},
    {"id": 2, "nome": "Poção de Cura", "preco": 50.00},
    {"id": 3, "nome": "Grimório de Feitiços", "preco": 200.00}
]

# Carrinho de compras (armazena produtos comprados por usuário)
carrinho = {}

# Função para processar a mensagem recebida
def processar_mensagem(mensagem):
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
        
        # Simula o cadastro de um novo usuário
        usuarios[email] = {"senha": senha, "nome": nome, "casa": casa, "tipo_bruxo": tipo_bruxo}
        return {'status': 'sucesso'}

    elif acao == 'visualizar_loja':
        # Simula a visualização da loja
        return {'status': 'sucesso', 'produtos': produtos_disponiveis}
    
    elif acao == 'adicionar_produto_carrinho':
        email = mensagem.get('email')
        produto_id = mensagem.get('produto_id')
        
        if email not in carrinho:
            carrinho[email] = []
        
        # Verifica se o produto existe
        produto = next((p for p in produtos_disponiveis if p['id'] == produto_id), None)
        if produto:
            carrinho[email].append(produto)
            return {'status': 'sucesso', 'produto_adicionado': produto}
        else:
            return {'erro': 'produto_nao_encontrado'}
    
    elif acao == 'visualizar_carrinho':
        email = mensagem.get('email')
        
        if email in carrinho:
            return {'status': 'sucesso', 'carrinho': carrinho[email]}
        else:
            return {'erro': 'carrinho_vazio'}
    
    return {'erro': 'acao_invalida'}

def iniciar_servidor(host='localhost', porta=5000):
    # Criação do socket
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, porta))
    servidor.listen(1)
    
    print(f"Servidor mock em execução em {host}:{porta}")
    
    while True:
        # Aceitar conexões de clientes
        cliente_socket, cliente_endereco = servidor.accept()
        print(f"Conexão recebida de {cliente_endereco}")
        
        try:
            # Receber a mensagem do cliente
            mensagem = cliente_socket.recv(1024).decode('utf-8')
            mensagem = json.loads(mensagem)
            print(f"Mensagem recebida: {mensagem}")
            
            # Processar a mensagem e enviar a resposta
            resposta = processar_mensagem(mensagem)
            resposta_json = json.dumps(resposta)
            cliente_socket.sendall(resposta_json.encode('utf-8'))
        
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
        
        finally:
            # Fechar a conexão com o cliente
            cliente_socket.close()

if __name__ == '__main__':
    iniciar_servidor()



