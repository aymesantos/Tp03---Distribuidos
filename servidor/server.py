import socket
import threading
import json
import funcionalidades

class Server:
  
    def __init__(self, host='localhost', porta=5000):
        self.host = host
        self.porta = porta
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.host, self.porta))
        self.servidor.listen(5)
        print(f"Servidor iniciado em {self.host}:{self.porta}")

    def iniciar(self):
        while True:
            cliente_socket, endereco = self.servidor.accept()
            print(f"Conexão de {endereco}")
            threading.Thread(target=self.tratar_cliente, args=(cliente_socket,)).start()

    def tratar_cliente(self, cliente_socket):
        with cliente_socket:
            while True:
                try:
                    dados = cliente_socket.recv(4096)
                    if not dados:
                        break

                    mensagem = json.loads(dados.decode('utf-8'))
                    resposta = self.processar_mensagem(mensagem)
                    cliente_socket.sendall(json.dumps(resposta).encode('utf-8'))

                except Exception as e:
                    print(f"Erro ao processar requisição: {e}")
                    break

    def processar_mensagem(self, mensagem):
        acao = mensagem.get('acao')

        if acao == 'login':
            return funcionalidades.fazer_login(mensagem.get('email'), mensagem.get('senha'))
        
        if acao == 'cadastro':
            return funcionalidades.fazer_cadastro(
                mensagem.get('nome'),
                mensagem.get('casa'),
                mensagem.get('email'),
                mensagem.get('senha'),
                mensagem.get('tipo_bruxo')
            )

        if acao == 'obter_perfil':
            return funcionalidades.obter_perfil(mensagem.get('email'))

        if acao == 'atualizar_perfil':
            return funcionalidades.atualizar_perfil(
                mensagem.get('nome'),
                mensagem.get('casa_hogwarts'),
                mensagem.get('tipo_bruxo'),
                mensagem.get('email')
            )

        # Loja
        if acao == 'criar_loja':
            return funcionalidades.criar_loja(mensagem.get('email'), mensagem.get('nome_loja'), mensagem.get('descricao'))

        if acao == 'editar_loja':
            return funcionalidades.editar_loja(mensagem.get('email'), mensagem.get('nome_loja'), mensagem.get('descricao'))

        if acao == 'obter_loja':
            return funcionalidades.obter_loja(mensagem.get('email'))

        # Produtos
        if acao == 'criar_produto':
            return funcionalidades.criar_produto(
                mensagem.get('email'),
                mensagem.get('nome'),
                mensagem.get('descricao'),
                mensagem.get('preco'),
                mensagem.get('categoria'),
                mensagem.get('imagens_base64')
            )

        if acao == 'editar_produto':
            return funcionalidades.editar_produto(
                mensagem.get('produto_id'),
                mensagem.get('nome'),
                mensagem.get('descricao'),
                mensagem.get('preco'),
                mensagem.get('categoria'),
                mensagem.get('status'),
                mensagem.get('imagem_base64')
            )

        if acao == 'listar_produtos':
            return funcionalidades.listar_produtos(mensagem.get('filtros'))

        if acao == 'listar_meus_produtos':
            return funcionalidades.listar_meus_produtos(mensagem.get('email'))

        if acao == 'obter_produto':
            return funcionalidades.obter_produto(mensagem.get('id_produto'))

        # Carrinho
        if acao == 'adicionar_produto_carrinho':
            return funcionalidades.adicionar_ao_carrinho(
                mensagem.get('email'),
                mensagem.get('produto_id'),
                mensagem.get('quantidade', 1)
            )

        if acao == 'remover_do_carrinho':
            return funcionalidades.remover_do_carrinho(mensagem.get('id_produto'))

        if acao == 'visualizar_carrinho':
            return funcionalidades.visualizar_carrinho(mensagem.get('email'))

        # Compras
        if acao == 'finalizar_compra':
            return funcionalidades.finalizar_compra(mensagem.get('email'))

        # Histórico
        if acao == 'historico_compras':
            return funcionalidades.historico_compras(mensagem.get('email'))

        if acao == 'historico_vendas':
            return funcionalidades.historico_vendas(mensagem.get('email'))

        return {'status': 'erro', 'mensagem': 'Ação inválida ou não implementada'}

if __name__ == "__main__":
    server = Server()
    server.iniciar()
