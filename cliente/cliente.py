import socket
import json
import threading
import base64
from io import BytesIO
from PIL import Image

class Cliente:
    def __init__(self, host='localhost', porta=5000):
        self.host = host
        self.porta = porta
        self.conectado = False
        self.socket = None
        self.usuario_logado = None
        self.token = None
        # Lock para sincronização de threads
        self.socket_lock = threading.Lock()
        self.conectar()
    
    def conectar(self):
        """Estabelece conexão com o servidor"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.porta))
            self.conectado = True
            return True
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")
            self.conectado = False
            return False
    
    def __enviar_com_timeout(self, mensagem, timeout=5):
        """Envia mensagem com timeout para evitar travamentos"""
        try:
            self.socket.settimeout(timeout)
            # Serializa a mensagem para JSON
            mensagem_json = json.dumps(mensagem)
            # Adiciona o token se existir e não for uma operação de login/cadastro
            if self.token and mensagem.get('acao') not in ['login', 'cadastro']:
                mensagem_json_obj = json.loads(mensagem_json)
                mensagem_json_obj['token'] = self.token
                mensagem_json = json.dumps(mensagem_json_obj)
            
            # Envia a mensagem como bytes
            self.socket.sendall(mensagem_json.encode('utf-8'))
            print(f"Enviando para o servidor: {mensagem_json}")

            return True
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            return False
        
    def __receber_com_timeout(self, timeout=5):
        """Recebe resposta com timeout para evitar travamentos"""
        try:
            self.socket.settimeout(timeout)
            resposta = self.socket.recv(4096)
            if not resposta:
                print("Erro: resposta vazia do servidor")
                return None
            mensagem = resposta.decode('utf-8').strip()
            if not mensagem:
                print("Erro: mensagem recebida é vazia")
                return None
            return json.loads(mensagem)
        except socket.timeout:
            print("Tempo de espera excedido ao receber resposta do servidor")
            return {"status": "erro", "erro": "timeout"}
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}")
            return None
        except Exception as e:
            print(f"Erro ao receber mensagem: {e}")
            return None

    
    def enviar_mensagem(self, mensagem):
        """Envia mensagem ao servidor com tratamento para reconexão"""
        with self.socket_lock:  # Garante exclusão mútua
            if not self.conectado:
                if not self.conectar():
                    return {"status": "erro", "erro": "conexao_falhou"}
            
            if not self.__enviar_com_timeout(mensagem):
                # Tenta reconectar uma vez
                if self.conectar():
                    if not self.__enviar_com_timeout(mensagem):
                        return {"status": "erro", "erro": "envio_falhou"}
                else:
                    return {"status": "erro", "erro": "conexao_falhou"}
            
            return self.__receber_com_timeout()
        
    def executar_operacao(self, operacao, callback=None, **params):
        """Executa operação em thread separada"""
        def executar():
            resultado = operacao(**params)
            if callback:
                callback(resultado)
            return resultado
        
        thread = threading.Thread(target=executar)
        thread.daemon = True
        thread.start()
        return thread
    
    # AUTENTICAÇÃO E CADASTRO
    
    def login(self, email, senha, callback=None):
        """Realiza login do usuário"""
        def operacao_login(email, senha):
            mensagem = {'acao': 'login', 'email': email, 'senha': senha}
            resposta = self.enviar_mensagem(mensagem)

            if resposta and resposta.get('status') == 'sucesso':
                self.usuario_logado = resposta.get('usuario')
                self.token = resposta.get('token')
            
            return resposta
        
        if callback:
            return self.executar_operacao(operacao_login, callback, email=email, senha=senha)
        else:
            return operacao_login(email, senha)
        

    def obter_dados_perfil(self, callback=None):
        """Obtém os dados do perfil do usuário logado"""
        def operacao_obter_perfil():
            print("=== DEBUG: Iniciando obter_dados_perfil ===")
            print(f"DEBUG: Usuario logado: {self.usuario_logado}")
            
            if not self.usuario_logado:
                return {"status": "erro", "erro": "usuario_nao_logado"}
            
            email = self.usuario_logado.get('email')
            
            if not email:
                return {"status": "erro", "erro": "email_nao_disponivel"}
            
            mensagem = {'acao': 'obter_perfil', 'email': email}
            
            resposta = self.enviar_mensagem(mensagem)
            
            if resposta and resposta.get('status') == 'sucesso':
                dados_perfil = resposta.get('dados_perfil', {})
                
                for chave, valor in dados_perfil.items():
                    self.usuario_logado[chave] = valor

                if 'casa' in self.usuario_logado and 'casa_hogwarts' not in self.usuario_logado:
                    self.usuario_logado['casa_hogwarts'] = self.usuario_logado['casa']
                    
                return self.usuario_logado
            else:
                print(f"DEBUG: Erro na resposta - {resposta}")
            
            print("=== DEBUG: Finalizando obter_dados_perfil ===")
            return resposta

        if callback:
            return self.executar_operacao(operacao_obter_perfil, callback)
        else:
            return operacao_obter_perfil()

        
    def atualizar_perfil(self, nome, casa_hogwarts, tipo_bruxo, email, callback=None):
        """Atualiza os dados do perfil do usuário no servidor"""
        def operacao_atualizar_perfil(nome, casa_hogwarts, tipo_bruxo, email):
            try:
                mensagem = {
                    'acao': 'atualizar_perfil',
                    'nome': nome,
                    'casa_hogwarts': casa_hogwarts,
                    'tipo_bruxo': tipo_bruxo,
                    'email': email
                }
                return self.enviar_mensagem(mensagem)
            except Exception as e:
                print(f"Erro ao atualizar perfil: {str(e)}")
                return {"status": "erro", "mensagem": str(e)}

        if callback:
            return self.executar_operacao(
                operacao_atualizar_perfil, callback,
                nome=nome, casa_hogwarts=casa_hogwarts, tipo_bruxo=tipo_bruxo
            )
        else:
            return operacao_atualizar_perfil(nome, casa_hogwarts, tipo_bruxo)


    def cadastro(self, nome, casa, email, senha, tipo_bruxo, callback=None):
        """Cadastra um novo usuário"""
        def operacao_cadastro(nome, casa, email, senha, tipo_bruxo):
            mensagem = {
                'acao': 'cadastro', 
                'nome': nome, 
                'casa': casa, 
                'email': email, 
                'senha': senha, 
                'tipo_bruxo': tipo_bruxo
            }
            return self.enviar_mensagem(mensagem)
        
        if callback:
            return self.executar_operacao(operacao_cadastro, callback, 
                                        nome=nome, casa=casa, email=email, 
                                        senha=senha, tipo_bruxo=tipo_bruxo)
        else:
            return operacao_cadastro(nome, casa, email, senha, tipo_bruxo)
    
    def logout(self):
        """Realiza logout do usuário e encerra a conexão"""
        # Fecha a conexão, se existir
        if hasattr(self, 'socket') and self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)  # opcional para uma finalização limpa
                self.socket.close()
            except Exception as e:
                print(f"Erro ao fechar conexão: {e}")

            self.socket = None

        self.usuario_logado = None
        self.token = None
        return {"status": "sucesso", "mensagem": "Logout realizado com sucesso"}

    
    # GERENCIAMENTO DE LOJA

    def criar_loja(self, nome_loja, descricao, callback=None):
        """Cria uma nova loja para o usuário (RF011)"""
        def operacao_criar_loja(nome_loja, descricao):
            mensagem = {
                'acao': 'criar_loja',
                'nome_loja': nome_loja,
                'descricao': descricao
            }
            return self.enviar_mensagem(mensagem)
        
        if callback:
            return self.executar_operacao(operacao_criar_loja, callback, 
                                        nome_loja=nome_loja, descricao=descricao)
        else:
            return operacao_criar_loja(nome_loja, descricao)

    def editar_loja(self, nome_loja=None, descricao=None, callback=None):
        """Edita informações da loja do usuário (RF012)"""
        def operacao_editar_loja(nome_loja, descricao):
            dados = {'acao': 'editar_loja'}
            
            if nome_loja:
                dados['nome_loja'] = nome_loja
            if descricao:
                dados['descricao'] = descricao
            
            return self.enviar_mensagem(dados)
        
        if callback:
            return self.executar_operacao(operacao_editar_loja, callback,
                                        nome_loja=nome_loja, descricao=descricao)
        else:
            return operacao_editar_loja(nome_loja, descricao)

    
    def obter_loja(self):
        try:
            mensagem = {'acao': 'obter_loja', 'email': self.usuario_logado['email']}
            resposta = self.enviar_mensagem(mensagem)
            print(f"Resposta da loja: {resposta}")
            if resposta and resposta.get('status') == 'sucesso':
                return {
                    'status': resposta['status'],
                    'nome_loja': resposta['nome_loja'],
                    'descricao': resposta['descricao'],
                    'produtos': resposta.get('produtos', [])
                }
            else:
                return resposta
        except Exception as e:
            print(f"Erro ao obter loja: {e}")
            return None

    
    # GERENCIAMENTO DE PRODUTOS
    
    def criar_produto(self, nome, descricao, preco, categoria, caminho_imagem=None, callback=None):
        """Cria um novo anúncio de produto (RF013)"""
        def operacao_criar_produto(nome, descricao, preco, categoria, caminho_imagem):
            imagens_base64 = None

            if caminho_imagem:
                try:
                    img_data = self.redimensionar_imagem(caminho_imagem)
                    if img_data:
                        imagens_base64 = base64.b64encode(img_data).decode('utf-8')
                except Exception as e:
                    print(f"Erro ao processar imagem do produto: {e}")

            mensagem = {
                'acao': 'criar_produto',
                'nome': nome,
                'descricao': descricao,
                'preco': preco,
                'categoria': categoria,
                'imagens_base64': imagens_base64
            }
            return self.enviar_mensagem(mensagem)

        if callback:
            return self.executar_operacao(operacao_criar_produto, callback,
                                        nome=nome, descricao=descricao,
                                        preco=preco, categoria=categoria,
                                        caminho_imagem=caminho_imagem)
        else:
            return operacao_criar_produto(nome, descricao, preco, categoria, caminho_imagem)


    def editar_produto(self, produto_id, nome,descricao, preco, categoria, status, caminho_imagem=None, callback=None):
        """Edita um produto existente, com imagem opcional"""
        def operacao_editar_produto(produto_id, nome,descricao, preco, categoria,status, caminho_imagem):
            imagem_base64 = None
            if caminho_imagem:
                try:
                    with open(caminho_imagem, 'rb') as img_file:
                        imagem_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                except Exception as e:
                    print(f"Erro ao abrir imagem: {e}")

            mensagem = {
                'acao': 'editar_produto',
                'produto_id': produto_id,
                'nome': nome,
                'descricao': descricao,
                'preco': preco,
                'categoria': categoria,
                'status': status,
                'imagem_base64': imagem_base64
            }
            return self.enviar_mensagem(mensagem)

        if callback:
            return self.executar_operacao(operacao_editar_produto, callback,
                                        produto_id=produto_id,
                                        nome=nome,
                                        descricao=descricao,
                                        preco=preco,
                                        categoria=categoria,
                                        status=status,
                                        caminho_imagem=caminho_imagem)
        else:
            return operacao_editar_produto(produto_id, nome, descricao, preco, categoria, status, caminho_imagem)

    
    def listar_produtos(self, filtros=None, callback=None):
        """Lista produtos disponíveis para compra (RF015)"""
        def operacao_listar_produtos(filtros):
            mensagem = {'acao': 'listar_produtos'}
            if filtros:
                mensagem['filtros'] = filtros
                print(f"[CLIENTE] Enviando mensagem de listagem: {mensagem}")  # DEBUG
            return self.enviar_mensagem(mensagem)
        
        if callback:
            return self.executar_operacao(operacao_listar_produtos, callback, filtros=filtros)
        else:
            return operacao_listar_produtos(filtros)
        
    def listar_meus_produtos(self):
        """Lista produtos da loja do usuário"""
        mensagem = {'acao': 'listar_meus_produtos', 'email': self.usuario_logado['email']}
        return self.enviar_mensagem(mensagem)

    
    def obter_detalhes_produto(self, id_produto, callback=None):
        """Obtém detalhes de um produto específico (RF015)"""
        def operacao_obter_produto(id_produto):
            mensagem = {
                'acao': 'obter_produto',
                'id_produto': id_produto
            }
            return self.enviar_mensagem(mensagem)
        
        if callback:
            return self.executar_operacao(operacao_obter_produto, callback, id_produto=id_produto)
        else:
            return operacao_obter_produto(id_produto)
    
    # GERENCIAMENTO DE CARRINHO
    
    def adicionar_ao_carrinho(self, id_produto, quantidade=1, callback=None):
        """Adiciona um produto ao carrinho"""
        def operacao_adicionar_carrinho(id_produto, quantidade):
            mensagem = {
                'acao': 'adicionar_produto_carrinho',  
                'email': self.usuario_logado['email'], 
                'produto_id': id_produto,
                'quantidade': quantidade
            }
            return self.enviar_mensagem(mensagem)
        
        if callback:
            return self.executar_operacao(operacao_adicionar_carrinho, callback,
                                        id_produto=id_produto, quantidade=quantidade)
        else:
            return operacao_adicionar_carrinho(id_produto, quantidade)

    
    def remover_do_carrinho(self, id_produto, callback=None):
        """Remove um produto do carrinho"""
        def operacao_remover_carrinho(id_produto):
            mensagem = {
                'acao': 'remover_do_carrinho',
                'id_produto': id_produto
            }
            return self.enviar_mensagem(mensagem)
        
        if callback:
            return self.executar_operacao(operacao_remover_carrinho, callback, id_produto=id_produto)
        else:
            return operacao_remover_carrinho(id_produto)
    
    def visualizar_carrinho(self, callback=None):
        """Visualiza os itens no carrinho de compras"""
        def operacao_visualizar_carrinho():
            mensagem = {'acao': 'visualizar_carrinho'}
            return self.enviar_mensagem(mensagem)
        
        if callback:
            return self.executar_operacao(operacao_visualizar_carrinho, callback)
        else:
            return operacao_visualizar_carrinho()
    
    # PAGAMENTO E FINALIZAÇÃO DE COMPRA
        
    def finalizar_compra(self, callback=None):
        def operacao_finalizar_compra():
            mensagem = {
                'acao': 'finalizar_compra',
                'email': self.usuario_logado['email']
            }
            return self.enviar_mensagem(mensagem)

        if callback:
            return self.executar_operacao(operacao_finalizar_compra, callback)
        else:
            return operacao_finalizar_compra()
 
    # HISTÓRICO DE TRANSAÇÕES
    
    def historico_compras(self, callback=None):
        def operacao_historico_compras():
            mensagem = {'acao': 'historico_compras', 'email': self.usuario_logado['email']}
            return self.enviar_mensagem(mensagem)
        
        if callback:
            return self.executar_operacao(operacao_historico_compras, callback)
        else:
            return operacao_historico_compras()

    def historico_vendas(self, callback=None):
        def operacao_historico_vendas():
            mensagem = {'acao': 'historico_vendas', 'email': self.usuario_logado['email']}
            return self.enviar_mensagem(mensagem)
        
        if callback:
            return self.executar_operacao(operacao_historico_vendas, callback)
        else:
            return operacao_historico_vendas()

    
    def encerrar(self):
        """Encerra a conexão com o servidor"""
        try:
            with self.socket_lock:
                if self.socket:
                    self.socket.close()
                self.conectado = False
        except Exception as e:
            print(f"Erro ao encerrar conexão: {e}")