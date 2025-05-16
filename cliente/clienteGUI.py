import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QMenu, QLabel, QLineEdit, 
                           QListWidget, QStackedWidget, QPushButton, QHBoxLayout, QMessageBox, 
                           QComboBox, QGridLayout, QFileDialog, QListWidgetItem, QScrollArea, 
                           QFrame, QTextEdit, QDialog, QDoubleSpinBox, QFormLayout, QSpinBox)
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QPainter, QImage, QFont, QColor, QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
import re
from cliente import Cliente
from PIL import Image
import io
import base64

# Constantes para estilo
FONTE_PRINCIPAL = "Verdana"
COR_FUNDO = "#1e2b2b"       # Fundo escuro
COR_TEXTO = "#e2c8a0"       # Texto dourado/bege
COR_DESTAQUE = "#e2c8a0"    # Botões em dourado/bege


class ProdutoItem(QWidget):
    """Widget personalizado para exibir um produto na lista"""
    comprar_clicado = pyqtSignal(dict)
    editar_clicado = pyqtSignal(dict)
    
    def __init__(self, produto, modo='comprar'):
        super().__init__()
        self.produto = produto
        self.modo = modo  # 'comprar' ou 'editar'
        self.initUI()
        
    def initUI(self):
        layout = QHBoxLayout()

        info_layout = QVBoxLayout()
        titulo = QLabel(f"<b>{self.produto.get('nome', 'Sem nome')}</b>")
        titulo.setFont(QFont(FONTE_PRINCIPAL, 12))

        preco = QLabel(f"R$ {self.produto.get('preco', 0):.2f}")
        preco.setFont(QFont(FONTE_PRINCIPAL, 10))
        preco.setStyleSheet(f"color: {COR_DESTAQUE};")

        descricao_texto = self.produto.get('descricao', 'Sem descrição')
        if len(descricao_texto) > 100:
            descricao_texto = descricao_texto[:100] + "..."
        descricao = QLabel(descricao_texto)
        descricao.setFont(QFont(FONTE_PRINCIPAL, 9))
        descricao.setWordWrap(True)

        info_layout.addWidget(titulo)
        info_layout.addWidget(preco)
        info_layout.addWidget(descricao)

        # Botão de ação
        if self.modo == 'comprar':
            acao_btn = QPushButton("Adicionar ao Carrinho")
            acao_btn.clicked.connect(lambda: self.comprar_clicado.emit(self.produto))
        else: 
            acao_btn = QPushButton("Editar")
            acao_btn.clicked.connect(lambda: self.editar_clicado.emit(self.produto))

        layout.addLayout(info_layout, 1)
        layout.addWidget(acao_btn)

        self.setLayout(layout)

class JanelaLogin(QWidget):
    """Tela de login do sistema"""
    def __init__(self):
        super().__init__()
        self.cliente = Cliente()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('BecoDiagonal - Login')
        self.setFixedSize(1366, 768)

        # Fundo com imagem usando QLabel
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("imagens/login.png"))
        self.background.setGeometry(0, 0, 1366, 768)

        # Campo de email
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('Email')
        self.email_input.setGeometry(850, 220, 422, 63)
        self.email_input.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0);
            border: none;
            color: white;
            font-size: 25px;
        """)

        # Campo de senha
        self.senha_input = QLineEdit(self)
        self.senha_input.setPlaceholderText('Senha')
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setGeometry(850, 333, 422, 63)
        self.senha_input.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0);
            border: none;
            color: white;
            font-size: 25px;
        """)

        # Botão de login
        self.login_btn = QPushButton('', self)
        self.login_btn.setGeometry(834, 446, 184, 63)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
            }
            QPushButton:hover {
                cursor: pointer-hand;
            }
        """)
        self.login_btn.clicked.connect(self.realizar_login)

        # Botão de cadastro
        self.cadastro_btn = QPushButton('', self)
        self.cadastro_btn.setGeometry(1072, 446, 184, 63)
        self.cadastro_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
            }
            QPushButton:hover {
                cursor: pointer-hand;
            }
        """)
        self.cadastro_btn.clicked.connect(self.ir_para_cadastro)
        
        self.show()

    def realizar_login(self):
        email = self.email_input.text().strip()
        senha = self.senha_input.text()

        if not email or not senha:
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos!')
            return

        resposta = self.cliente.login(email, senha)

        if resposta:
            if resposta.get('status') == 'sucesso':
                self.usuario_logado = resposta.get('usuario')
                QMessageBox.information(self, 'Sucesso', 'Login realizado com sucesso!')
                self.abrir_marketplace()
            elif resposta.get('erro') == 'senha_incorreta':
                QMessageBox.warning(self, 'Erro', 'Senha incorreta!')
            elif resposta.get('erro') == 'usuario_nao_encontrado':
                QMessageBox.warning(self, 'Erro', 'Usuário não encontrado!')
            else:
                QMessageBox.warning(self, 'Erro', 'Erro no login.')
        else:
            QMessageBox.warning(self, 'Erro', 'Erro de conexão com o servidor.')

    def abrir_marketplace(self):
        self.close()
        self.marketplace = JanelaMarketplace(self.cliente)
        self.marketplace.show()

    def ir_para_cadastro(self):
        self.close()
        self.janela_cadastro = JanelaCadastro(self.cliente)
        self.janela_cadastro.show()

class JanelaCadastro(QWidget):
    """Tela de cadastro de usuário"""
    def __init__(self, cliente):
        super().__init__()
        self.cliente = cliente
        self.initUI()

    def initUI(self):
        self.setWindowTitle('BecoDiagonal - Cadastro')
        self.setFixedSize(1366, 768)

        # Imagem de fundo
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("imagens/cadastro.png"))
        self.background.setGeometry(0, 0, 1366, 768)

        # Campo nome
        self.nome_input = QLineEdit(self)
        self.nome_input.setPlaceholderText("Nome completo")
        self.nome_input.setGeometry(860, 94, 422, 63)  
        self.nome_input.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0);
            border: none;
            color: white;
            font-size: 22px;
        """)

        # Botão de seleção de casa
        self.casa_input = QPushButton("Selecionar casa", self)
        self.casa_input.setGeometry(860, 199, 422, 63)
        self.casa_input.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
                color: white;
                font-size: 22px;
                text-align: left;
                padding-left: 10px;
            }
        """)

        # Menu com as opções
        self.casa_menu = QMenu(self)
        for casa in ["Grifinória", "Sonserina", "Corvinal", "Lufa-Lufa"]:
            action = self.casa_menu.addAction(casa)
            action.triggered.connect(lambda checked, casa=casa: self.casa_input.setText(casa))

        self.casa_input.setMenu(self.casa_menu)

        # Campo email
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Email")
        self.email_input.setGeometry(860, 304, 422, 63)  
        self.email_input.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0);
            border: none;
            color: white;
            font-size: 22px;
        """)

        # Campo senha
        self.senha_input = QLineEdit(self)
        self.senha_input.setPlaceholderText("Senha")
        self.senha_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.senha_input.setGeometry(860, 409, 422, 63)  
        self.senha_input.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0);
            border: none;
            color: white;
            font-size: 22px;
        """)

        # Botão de seleção de tipo de bruxo
        self.tipo_bruxo_input = QPushButton("Selecionar tipo de bruxo", self)
        self.tipo_bruxo_input.setGeometry(860, 514, 422, 63)
        self.tipo_bruxo_input.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
                color: white;
                font-size: 22px;
                text-align: left;
                padding-left: 10px;
            }
        """)

        # Menu com as opções
        self.tipo_bruxo_menu = QMenu(self)
        for tipo in ["Sangue-puro", "Nascido-trouxa", "Aborto"]:
            action = self.tipo_bruxo_menu.addAction(tipo)
            action.triggered.connect(lambda checked, tipo=tipo: self.tipo_bruxo_input.setText(tipo))

        self.tipo_bruxo_input.setMenu(self.tipo_bruxo_menu)

        # Botão de cadastro
        self.cadastrar_btn = QPushButton('', self)
        self.cadastrar_btn.setGeometry(960, 619, 184, 63)  
        self.cadastrar_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
            }
            QPushButton:hover {
                cursor: pointer-hand;
            }
        """)
        self.cadastrar_btn.clicked.connect(self.realizar_cadastro)

        # Botão voltar
        self.voltar_btn = QPushButton('Voltar', self)
        self.voltar_btn.setGeometry(100, 700, 100, 40)
        self.voltar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4b0082;
                color: white;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #6a0dad;
            }
        """)
        self.voltar_btn.clicked.connect(self.voltar_login)
        
        self.show()

    def voltar_login(self):
        self.close()
        self.janela_login = JanelaLogin()
        self.janela_login.show()

    def realizar_cadastro(self):
        nome = self.nome_input.text().strip()
        casa = self.casa_input.text().strip() 
        email = self.email_input.text().strip()
        senha = self.senha_input.text()
        tipo_bruxo = self.tipo_bruxo_input.text().strip()

        # Verificações locais conforme RF006 e RF007
        if not all([nome, email, senha]):
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos!')
            return
        
        if casa == "Selecionar casa" or tipo_bruxo == "Selecionar tipo de bruxo":
            QMessageBox.warning(self, 'Erro', 'Selecione uma casa e o tipo de bruxo.')
            return

        # Verificação RF006: nome deve ter entre 3 e 20 caracteres, com pelo menos uma letra
        if not re.match(r'^[A-Za-z0-9 ]{3,20}$', nome) or not any(c.isalpha() for c in nome):
            QMessageBox.warning(self, 'Erro', 'Nome deve ter entre 3 e 20 caracteres, conter pelo menos uma letra, e apenas letras, números e espaços.')
            return

        # Verificação RF007: senha deve ter no mínimo 8 caracteres
        if len(senha) < 8:
            QMessageBox.warning(self, 'Erro', 'A senha deve ter no mínimo 8 caracteres.')
            return

        # Verificação de email válido
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            QMessageBox.warning(self, 'Erro', 'Email inválido.')
            return

        resposta = self.cliente.cadastro(nome, casa, email, senha, tipo_bruxo)

        if resposta:
            if resposta.get('status') == 'sucesso':
                # Cadastro deu certo, agora tenta login automático
                resposta_login = self.cliente.login(email, senha)
                if resposta_login and resposta_login.get('status') == 'sucesso':
                    # Atualiza dados do cliente com usuário logado, token e email
                    self.cliente.usuario_logado = resposta_login.get('usuario')
                    self.cliente.token = resposta_login.get('token')
                    self.cliente.email = email

                    QMessageBox.information(self, 'Sucesso', 'Cadastro e login realizados com sucesso!')
                    self.voltar_login()
                else:
                    QMessageBox.warning(self, 'Erro', 'Cadastro realizado, mas falha no login automático. Tente fazer login manualmente.')
            elif resposta.get('erro') == 'email_ja_cadastrado':
                QMessageBox.warning(self, 'Erro', 'Email já cadastrado.')
            else:
                QMessageBox.warning(self, 'Erro', f'Erro no cadastro: {resposta.get("mensagem", "Tente novamente!")}')
        else:
            QMessageBox.warning(self, 'Erro', 'Erro de conexão com o servidor.')


class JanelaPerfilUsuario(QDialog):
    """Janela para visualizar o perfil do usuário"""
    def __init__(self, cliente):
        super().__init__()
        self.cliente = cliente
        self.initUI()
        self.carregar_dados_usuario()
    
    def initUI(self):
        self.setWindowTitle("Perfil do Usuário")
        self.setFixedSize(500, 550) 
        self.setStyleSheet("""
            QWidget {
                background-color: #1e2b2b;
                color: #e2c8a0;
            }
            QPushButton {
                background-color: #e2c8a0;
                color: #333333;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0b68e;
            }
            QLineEdit {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QScrollArea {
                border: 1px solid #152121;
                border-radius: 5px;
            }
            QLabel {
                color: #e2c8a0;
            }
            QFrame {
                background-color: #1e2b2b;
            }
        """)
        
        layout_principal = QVBoxLayout()
        
        # Título
        titulo = QLabel("Perfil do Bruxo")
        titulo.setFont(QFont(FONTE_PRINCIPAL, 18, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(titulo)
        
        # Informações do usuário
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            border: 1px solid #e2c8a0;
            border-radius: 15px;
            padding: 10px;
        """)
        
        info_layout = QVBoxLayout(info_frame)
        
        # Nome
        nome_layout = QHBoxLayout()
        nome_titulo = QLabel("Nome:")
        nome_titulo.setFont(QFont(FONTE_PRINCIPAL, 12, QFont.Weight.Bold))
        self.nome_valor = QLabel("Carregando...")
        self.nome_valor.setFont(QFont(FONTE_PRINCIPAL, 12))
        
        nome_layout.addWidget(nome_titulo)
        nome_layout.addWidget(self.nome_valor)
        info_layout.addLayout(nome_layout)
        
        # Casa de Hogwarts
        casa_layout = QHBoxLayout()
        casa_titulo = QLabel("Casa de Hogwarts:")
        casa_titulo.setFont(QFont(FONTE_PRINCIPAL, 12, QFont.Weight.Bold))
        self.casa_valor = QLabel("Carregando...")
        self.casa_valor.setFont(QFont(FONTE_PRINCIPAL, 12))
        
        casa_layout.addWidget(casa_titulo)
        casa_layout.addWidget(self.casa_valor)
        info_layout.addLayout(casa_layout)
        
        # Tipo de Bruxo
        tipo_layout = QHBoxLayout()
        tipo_titulo = QLabel("Tipo de Bruxo:")
        tipo_titulo.setFont(QFont(FONTE_PRINCIPAL, 12, QFont.Weight.Bold))
        self.tipo_valor = QLabel("Carregando...")
        self.tipo_valor.setFont(QFont(FONTE_PRINCIPAL, 12))
        
        tipo_layout.addWidget(tipo_titulo)
        tipo_layout.addWidget(self.tipo_valor)
        info_layout.addLayout(tipo_layout)
        
        layout_principal.addWidget(info_frame)
        
        # Botões
        botoes_layout = QHBoxLayout()

        # Botão Histórico de Compras
        self.historico_vendas_btn = QPushButton("Histórico de Compras")
        self.historico_vendas_btn.setFont(QFont(FONTE_PRINCIPAL, 11))
        self.historico_vendas_btn.clicked.connect(self.abrir_historico_vendas)
        botoes_layout.addWidget(self.historico_vendas_btn)
    
        # Botão Fechar
        fechar_btn = QPushButton("Fechar")
        fechar_btn.setFont(QFont(FONTE_PRINCIPAL, 11))
        fechar_btn.clicked.connect(self.reject)
        botoes_layout.addWidget(fechar_btn)
        
        layout_principal.addLayout(botoes_layout)
        
        self.setLayout(layout_principal)
    
    def carregar_dados_usuario(self):
        """Carrega os dados do usuário do cliente"""
        try:
            dados = self.cliente.obter_dados_perfil()
            print(f"DEBUG: Dados recebidos na interface: {dados}")
            
            if not dados or (isinstance(dados, dict) and dados.get('status') == 'erro'):
                raise Exception(f"Dados inválidos: {dados}")
                
            if 'nome' in dados:
                self.nome_valor.setText(dados["nome"])
            else:
                self.nome_valor.setText("Não disponível")
                
            if 'casa_hogwarts' in dados:
                self.casa_valor.setText(dados["casa_hogwarts"])
            elif 'casa' in dados:
                self.casa_valor.setText(dados["casa"])
            else:
                self.casa_valor.setText("Não disponível")
                
            if 'tipo_bruxo' in dados:
                self.tipo_valor.setText(dados["tipo_bruxo"])
            else:
                self.tipo_valor.setText("Não disponível")
            
        except Exception as e:
            print(f"ERRO: {str(e)}")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar dados do perfil: {str(e)}")
            self.nome_valor.setText("Erro ao carregar")
            self.casa_valor.setText("Erro ao carregar")
            self.tipo_valor.setText("Erro ao carregar")

    def abrir_historico_vendas(self):
        janela_historico = JanelaHistoricoCompras(self.cliente)
        janela_historico.exec()

class JanelaCriarLoja(QDialog):
    """Janela para criar ou editar uma loja"""
    def __init__(self, cliente, loja_dados=None):
        super().__init__()
        self.cliente = cliente
        self.loja_dados = loja_dados  # Se None, é criação; se tem dados, é edição
        self.initUI()
        
    def initUI(self):
        modo = "Editar" if self.loja_dados else "Criar"
        self.setWindowTitle(f"{modo} Loja")
        self.setFixedSize(600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e2b2b;
                color: #e2c8a0;
            }
            QPushButton {
                background-color: #e2c8a0;
                color: #333333;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0b68e;
            }
            QLineEdit {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QComboBox {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QScrollArea {
                border: 1px solid #152121;
                border-radius: 5px;
            }
            QLabel {
                color: #e2c8a0;
            }
            QFrame {
                background-color: #1e2b2b;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel(f"{modo} Loja")
        titulo.setFont(QFont(FONTE_PRINCIPAL, 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Nome da loja
        layout.addWidget(QLabel("Nome da Loja:"))
        self.nome_loja_input = QLineEdit()
        if self.loja_dados:
            self.nome_loja_input.setText(self.loja_dados.get('nome_loja', ''))
        layout.addWidget(self.nome_loja_input)
        
        # Descrição da loja
        layout.addWidget(QLabel("Descrição:"))
        self.descricao_input = QTextEdit()
        if self.loja_dados:
            self.descricao_input.setText(self.loja_dados.get('descricao', ''))
        self.descricao_input.setMaximumHeight(100)
        layout.addWidget(self.descricao_input)
        
        # Botões
        botoes_layout = QHBoxLayout()
        salvar_btn = QPushButton("Salvar")
        salvar_btn.clicked.connect(self.salvar_loja)
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        
        botoes_layout.addWidget(salvar_btn)
        botoes_layout.addWidget(cancelar_btn)
        layout.addLayout(botoes_layout)
        
        self.setLayout(layout)
    
    def salvar_loja(self):
        nome_loja = self.nome_loja_input.text().strip()
        descricao = self.descricao_input.toPlainText().strip()
        
        if not nome_loja:
            QMessageBox.warning(self, "Erro", "O nome da loja é obrigatório.")
            return
        
        if not descricao:
            QMessageBox.warning(self, "Erro", "A descrição da loja é obrigatória.")
            return

        if self.loja_dados:
            resposta = self.cliente.editar_loja(
                nome_loja=nome_loja, 
                descricao=descricao
            )
        else:
            resposta = self.cliente.criar_loja(
                nome_loja=nome_loja,
                descricao=descricao
            )
        
        if resposta and resposta.get('status') == 'sucesso':
            QMessageBox.information(self, "Sucesso", f"Loja {'atualizada' if self.loja_dados else 'criada'} com sucesso!")
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", f"Erro ao {'atualizar' if self.loja_dados else 'criar'} a loja: {resposta.get('mensagem', 'Tente novamente')}")

class JanelaCriarProduto(QDialog):
    """Janela para criar um novo produto ou editar existente"""
    def __init__(self, cliente, produto_dados=None):
        super().__init__()
        self.cliente = cliente
        self.produto_dados = produto_dados
        self.initUI()
        
    def initUI(self):
        modo = "Editar" if self.produto_dados else "Criar"
        self.setWindowTitle(f"{modo} Produto")
        self.setFixedSize(600, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e2b2b;
                color: #e2c8a0;
            }
            QPushButton {
                background-color: #e2c8a0;
                color: #333333;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0b68e;
            }
            QLineEdit {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QComboBox {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QScrollArea {
                border: 1px solid #152121;
                border-radius: 5px;
            }
            QLabel {
                color: #e2c8a0;
            }
            QFrame {
                background-color: #1e2b2b;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel(f"{modo} Produto")
        titulo.setFont(QFont(FONTE_PRINCIPAL, 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Nome do produto
        layout.addWidget(QLabel("Título do Produto:"))
        self.nome_input = QLineEdit()
        if self.produto_dados:
            self.nome_input.setText(self.produto_dados.get('nome', ''))
        layout.addWidget(self.nome_input)
        
        # Descrição
        layout.addWidget(QLabel("Descrição:"))
        self.descricao_input = QTextEdit()
        if self.produto_dados:
            self.descricao_input.setText(self.produto_dados.get('descricao', ''))
        self.descricao_input.setMaximumHeight(100)
        layout.addWidget(self.descricao_input)
        
        # Preço
        layout.addWidget(QLabel("Preço (R$):"))
        self.preco_input = QDoubleSpinBox()
        self.preco_input.setRange(0.01, 99999.99)
        self.preco_input.setDecimals(2)
        self.preco_input.setValue(float(self.produto_dados.get('preco', 1.00)) if self.produto_dados else 1.00)
        layout.addWidget(self.preco_input)
        
        # Categoria
        layout.addWidget(QLabel("Categoria:"))
        self.categoria_input = QComboBox()
        categorias = ["Livros", "Varinhas", "Vestes", "Animais", "Poções", "Outros"]
        self.categoria_input.addItems(categorias)
        if self.produto_dados:
            index = self.categoria_input.findText(self.produto_dados.get('categoria', ''))
            if index >= 0:
                self.categoria_input.setCurrentIndex(index)
        layout.addWidget(self.categoria_input)

        # Status 
        if self.produto_dados:
            layout.addWidget(QLabel("Status do Produto:"))
            self.status_input = QComboBox()
            self.status_input.addItems(["ativo", "pausado", "desativado", "vendido"])
            index = self.status_input.findText(self.produto_dados.get('status', 'ativo'))
            if index >= 0:
                self.status_input.setCurrentIndex(index)
            layout.addWidget(self.status_input)
        
        # Botões
        botoes_layout = QHBoxLayout()
        salvar_btn = QPushButton("Salvar")
        salvar_btn.clicked.connect(self.salvar_produto)
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        botoes_layout.addWidget(salvar_btn)
        botoes_layout.addWidget(cancelar_btn)
        layout.addLayout(botoes_layout)
        
        self.setLayout(layout)

    def salvar_produto(self):
        nome = self.nome_input.text().strip()
        descricao = self.descricao_input.toPlainText().strip()
        preco = self.preco_input.value()
        categoria = self.categoria_input.currentText()
        
        if not nome or not descricao:
            QMessageBox.warning(self, "Erro", "O título e a descrição são obrigatórios.")
            return
        
        if preco <= 0:
            QMessageBox.warning(self, "Erro", "O preço deve ser maior que zero.")
            return

        if self.produto_dados:
            status = self.status_input.currentText()
            resposta = self.cliente.editar_produto(
                produto_id=self.produto_dados.get('id'),
                nome=nome,
                descricao=descricao,
                preco=preco,
                categoria=categoria,
                status=status
            )
        else:
            resposta = self.cliente.criar_produto(
                nome=nome,
                descricao=descricao,
                preco=preco,
                categoria=categoria
            )
        
        if resposta and resposta.get('status') == 'sucesso':
            QMessageBox.information(self, "Sucesso", f"Produto {'atualizado' if self.produto_dados else 'criado'} com sucesso!")
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", f"Erro ao {'atualizar' if self.produto_dados else 'criar'} o produto: {resposta.get('mensagem', 'Tente novamente')}")

class JanelaMarketplace(QWidget):
    """Tela principal do marketplace com navegação entre seções"""
    def __init__(self, cliente):
        super().__init__()
        self.cliente = cliente
        self.carrinho = [] 
        self.initUI()
        self.carregar_produtos()
        
    def initUI(self):
        self.setWindowTitle('BecoDiagonal - Marketplace')
        self.setFixedSize(1366, 768)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1e2b2b;
                color: #e2c8a0;
            }
            QPushButton {
                background-color: #e2c8a0;
                color: #333333;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0b68e;
            }
            QLineEdit {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QScrollArea {
                border: 1px solid #152121;
                border-radius: 5px;
            }
            QLabel {
                color: #e2c8a0;
            }
            QFrame {
                background-color: #1e2b2b;
            }
        """)
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Barra superior com logo, busca e botões
        top_bar = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("imagens/logo_pequeno.png")
        logo_label.setPixmap(logo_pixmap.scaled(150, 50, Qt.AspectRatioMode.KeepAspectRatio))
        top_bar.addWidget(logo_label)
        
        # Campo de busca
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("Buscar produtos...")
        self.busca_input.returnPressed.connect(self.buscar_produtos)
        top_bar.addWidget(self.busca_input, 1)
        
        # Botão de busca
        buscar_btn = QPushButton("Buscar")
        buscar_btn.clicked.connect(self.buscar_produtos)
        top_bar.addWidget(buscar_btn)
        
        # Botão perfil
        perfil_btn = QPushButton("Meu Perfil")
        perfil_btn.clicked.connect(self.abrir_perfil)
        top_bar.addWidget(perfil_btn)
        
        # Botão minha loja
        minha_loja_btn = QPushButton("Minha Loja")
        minha_loja_btn.clicked.connect(self.abrir_minha_loja)
        top_bar.addWidget(minha_loja_btn)
        
        # Botão carrinho
        carrinho_btn = QPushButton("Carrinho (0)")
        carrinho_btn.clicked.connect(self.abrir_carrinho)
        self.carrinho_btn = carrinho_btn
        top_bar.addWidget(carrinho_btn)
        
        # Botão sair
        sair_btn = QPushButton("Sair")
        sair_btn.clicked.connect(self.fazer_logout)
        top_bar.addWidget(sair_btn)
        
        main_layout.addLayout(top_bar)
        
        # Menu de categorias
        categorias_layout = QHBoxLayout()
        categorias = ["Todos", "Livros", "Varinhas", "Vestes", "Animais", "Poções", "Outros"]
        
        for categoria in categorias:
            cat_btn = QPushButton(categoria)
            cat_btn.setObjectName(f"cat_{categoria.lower()}")
            cat_btn.clicked.connect(lambda checked, cat=categoria: self.filtrar_por_categoria(cat))
            categorias_layout.addWidget(cat_btn)
        
        main_layout.addLayout(categorias_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.produtos_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        
        main_layout.addWidget(self.scroll_area)
        
        self.setLayout(main_layout)

    def carregar_produtos(self, categoria=None, termo_busca=None):
        """Carrega os produtos do servidor com filtros opcionais"""
        print(f"Carregando produtos com categoria: {categoria}, termo de busca: {termo_busca}")
        
        while self.produtos_layout.count():
            item = self.produtos_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        resposta = self.cliente.listar_produtos(filtros={'categoria': categoria, 'termo_busca': termo_busca})
        print(resposta)

        if resposta and resposta.get('status') == 'sucesso':
            produtos = resposta.get('produtos', [])
            print(f"Produtos encontrados: {len(produtos)}")  
            
            if not produtos:
                info_label = QLabel("Nenhum produto encontrado.")
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                info_label.setStyleSheet("font-size: 16px; padding: 20px; color: #e2c8a0;")
                self.produtos_layout.addWidget(info_label)
            else:
                for produto in produtos:
                    produto_widget = ProdutoItem(produto, modo='comprar')
                    produto_widget.comprar_clicado.connect(self.adicionar_ao_carrinho)
                    self.produtos_layout.addWidget(produto_widget)

                    linha = QFrame()
                    linha.setFrameShape(QFrame.Shape.HLine)
                    linha.setFrameShadow(QFrame.Shadow.Sunken)
                    linha.setStyleSheet("background-color: #152121;")
                    self.produtos_layout.addWidget(linha)
        else:
            erro_label = QLabel("Erro ao carregar produtos. Tente novamente.")
            erro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            erro_label.setStyleSheet("font-size: 16px; color: #ff6b6b; padding: 20px;")
            self.produtos_layout.addWidget(erro_label)

    def buscar_produtos(self):
        """Busca produtos com o termo digitado"""
        termo = self.busca_input.text().strip()
        self.carregar_produtos(termo_busca=termo)
    
    def filtrar_por_categoria(self, categoria):
        """Filtra produtos por categoria"""
        if categoria == "Todos":
            categoria = None
        self.carregar_produtos(categoria=categoria)
    
    def adicionar_ao_carrinho(self, produto):
        """Adiciona um produto ao carrinho de compras"""
        produto_id = produto['id']

        for item in self.carrinho:
            if item['id'] == produto_id:
                QMessageBox.information(self, "Aviso", "Este produto já está no seu carrinho.")
                return

        resposta = self.cliente.adicionar_ao_carrinho(produto_id)
        if resposta and resposta.get('status') == 'sucesso':
            self.carrinho.append(produto)
            QMessageBox.information(self, "Sucesso", f"'{produto['nome']}' adicionado ao carrinho!")
            self.carrinho_btn.setText(f"Carrinho ({len(self.carrinho)})")
        else:
            QMessageBox.warning(self, "Erro", "Não foi possível adicionar o produto ao carrinho.")

    
    def abrir_carrinho(self):
        """Abre a janela do carrinho de compras"""
        dialog = JanelaCarrinho(self.cliente, self.carrinho)
        dialog.setStyleSheet(self.styleSheet())
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            self.carrinho = dialog.carrinho
            self.carrinho_btn.setText(f"Carrinho ({len(self.carrinho)})")
            
            if dialog.compra_finalizada:
                self.carregar_produtos()
    
    def abrir_perfil(self):
        """Abre a janela de edição do perfil do usuário"""
        dialog = JanelaPerfilUsuario(self.cliente)
        dialog.setStyleSheet(self.styleSheet())
        dialog.exec()
    
    def abrir_minha_loja(self):
        """Abre a janela da loja do usuário"""
        resposta = self.cliente.obter_loja()
        print(f"Resposta da loja (tipo: {type(resposta)}): {resposta}")
        
        if resposta:
            if resposta.get('status') == 'sucesso':
                loja_data = resposta
                janela_loja = JanelaMinhaLoja(self.cliente, loja_data)
                janela_loja.setStyleSheet(self.styleSheet())
                janela_loja.exec()
            
            elif resposta.get('erro') == 'loja_nao_encontrada':
                print("Loja não encontrada, perguntando se usuário deseja criar.")
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Criar Loja")
                msg_box.setText("Você ainda não possui uma loja. Deseja criar agora?")
                msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                reply = msg_box.exec()
                
                if reply == QMessageBox.StandardButton.Yes:
                    dialog = JanelaCriarLoja(self.cliente)
                    dialog.setStyleSheet(self.styleSheet())
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        print("Loja criada com sucesso, reabrindo janela da loja.")
                        self.abrir_minha_loja()
                else:
                    print("Usuário optou por não criar a loja.")
            
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Erro")
                msg_box.setText("Erro ao acessar informações da loja.")
                msg_box.exec()
        
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Erro")
            msg_box.setText("Erro ao acessar informações da loja X")
            msg_box.exec()

        
    def fazer_logout(self):
        """Encerra a sessão do usuário e volta para a tela de login"""
        resposta = self.cliente.logout()
        
        if resposta and resposta.get('status') == 'sucesso':
            self.close()
            self.janela_login = JanelaLogin()
            self.janela_login.show()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Erro")
            msg_box.setText("Erro ao realizar logout.")
            msg_box.exec()


class JanelaCarrinho(QDialog):
    """Janela do carrinho de compras"""
    def __init__(self, cliente, carrinho):
        super().__init__()
        self.cliente = cliente
        self.carrinho = carrinho.copy()
        self.compra_finalizada = False
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Carrinho de Compras")
        self.setFixedSize(800, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e2b2b;
                color: #e2c8a0;
            }
            QPushButton {
                background-color: #e2c8a0;
                color: #333333;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0b68e;
            }
            QLineEdit {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QScrollArea {
                border: 1px solid #152121;
                border-radius: 5px;
            }
            QLabel {
                color: #e2c8a0;
            }
            QFrame {
                background-color: #1e2b2b;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("Seu Carrinho de Compras")
        titulo.setFont(QFont(FONTE_PRINCIPAL, 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        if not self.carrinho:
            info_label = QLabel("Seu carrinho está vazio.")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_label.setStyleSheet("font-size: 16px; padding: 20px;")
            layout.addWidget(info_label)
        else:
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_widget = QWidget()
            self.itens_layout = QVBoxLayout(scroll_widget)

            total = 0
            for produto in self.carrinho:
                item_widget = self.criar_item_carrinho(produto)
                self.itens_layout.addWidget(item_widget)
  
                linha = QFrame()
                linha.setFrameShape(QFrame.Shape.HLine)
                linha.setFrameShadow(QFrame.Shadow.Sunken)
                self.itens_layout.addWidget(linha)
                
                total += float(produto['preco'])
            
            scroll_area.setWidget(scroll_widget)
            layout.addWidget(scroll_area)

            self.total_label = QLabel(f"Total: R$ {total:.2f}")
            self.total_label.setFont(QFont(FONTE_PRINCIPAL, 14, QFont.Weight.Bold))
            self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(self.total_label)
            
            # Botão finalizar compra
            finalizar_btn = QPushButton("Finalizar Compra")
            finalizar_btn.clicked.connect(self.finalizar_compra)
            layout.addWidget(finalizar_btn)
        
        # Botão voltar
        voltar_btn = QPushButton("Voltar ao Marketplace")
        voltar_btn.clicked.connect(self.accept)
        layout.addWidget(voltar_btn)
        
        self.setLayout(layout)
    
    def criar_item_carrinho(self, produto):
        """Cria um widget para um item do carrinho"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Informações do produto
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        titulo = QLabel(produto['nome'])
        titulo.setFont(QFont(FONTE_PRINCIPAL, 12, QFont.Weight.Bold))
        
        preco = QLabel(f"R$ {float(produto['preco']):.2f}")
        preco.setFont(QFont(FONTE_PRINCIPAL, 11))
        
        info_layout.addWidget(titulo)
        info_layout.addWidget(preco)
        
        layout.addWidget(info_widget, 1)
        
        # Botão remover
        remover_btn = QPushButton("Remover")
        remover_btn.clicked.connect(lambda: self.remover_do_carrinho(produto))
        layout.addWidget(remover_btn)
        
        return widget
    
    def remover_do_carrinho(self, produto):
        """Remove um produto do carrinho"""
        self.carrinho = [p for p in self.carrinho if p['id'] != produto['id']]
        self.accept() 
        self.done(QDialog.DialogCode.Accepted)
    
    def finalizar_compra(self):
        """Finaliza a compra dos itens no carrinho"""
        if not self.carrinho:
            QMessageBox.warning(self, "Erro", "Seu carrinho está vazio.")
            return

        reply = QMessageBox.question(self, 'Finalizar Compra', 
                                     'Confirma a compra destes itens?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            produtos_ids = [p['id'] for p in self.carrinho]
            resposta = self.cliente.finalizar_compra()
            
            if resposta and resposta.get('status') == 'sucesso':
                QMessageBox.information(self, "Sucesso", "Compra realizada com sucesso!")
                self.carrinho = []
                self.compra_finalizada = True
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", f"Erro ao finalizar compra: {resposta.get('mensagem', 'Tente novamente')}")


class JanelaMinhaLoja(QDialog):
    """Janela para gerenciar a loja do usuário"""
    def __init__(self, cliente, loja_dados):
        super().__init__()
        self.cliente = cliente
        self.loja_dados = loja_dados
        self.initUI()
        self.carregar_produtos()
        
    def initUI(self):
        self.setWindowTitle(f"Minha Loja - {self.loja_dados['nome_loja']}")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout()

        info_layout = QHBoxLayout()

        detalhes_layout = QVBoxLayout()
        
        nome_loja = QLabel(self.loja_dados['nome_loja'])
        nome_loja.setFont(QFont(FONTE_PRINCIPAL, 16, QFont.Weight.Bold))
        
        descricao = QLabel(self.loja_dados['descricao'])
        descricao.setWordWrap(True)
        
        detalhes_layout.addWidget(nome_loja)
        detalhes_layout.addWidget(descricao)
        
        info_layout.addLayout(detalhes_layout, 1)
        
        # Botão editar loja
        editar_loja_btn = QPushButton("Editar Loja")
        editar_loja_btn.clicked.connect(self.editar_loja)
        info_layout.addWidget(editar_loja_btn, alignment=Qt.AlignmentFlag.AlignTop)
        
        layout.addLayout(info_layout)

        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(linha)

        titulo_produtos = QLabel("Meus Produtos")
        titulo_produtos.setFont(QFont(FONTE_PRINCIPAL, 14, QFont.Weight.Bold))
        layout.addWidget(titulo_produtos)
        
        # Botão adicionar produto
        adicionar_produto_btn = QPushButton("Adicionar Novo Produto")
        adicionar_produto_btn.clicked.connect(self.adicionar_produto)
        layout.addWidget(adicionar_produto_btn)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.produtos_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)
        
        # Botões de navegação
        botoes_layout = QHBoxLayout()
        
        historico_btn = QPushButton("Ver Histórico de Vendas")
        historico_btn.clicked.connect(self.ver_historico)
        
        fechar_btn = QPushButton("Fechar")
        fechar_btn.clicked.connect(self.accept)
        
        botoes_layout.addWidget(historico_btn)
        botoes_layout.addWidget(fechar_btn)
        
        layout.addLayout(botoes_layout)
        
        self.setLayout(layout)
    
    def carregar_produtos(self):
        """Carrega os produtos da loja do usuário"""
        while self.produtos_layout.count():
            item = self.produtos_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        resposta = self.cliente.listar_meus_produtos()
        
        if resposta and resposta.get('status') == 'sucesso':
            produtos = resposta.get('produtos', [])
            
            if not produtos:
                info_label = QLabel("Você ainda não tem produtos cadastrados.")
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                info_label.setStyleSheet("font-size: 14px; padding: 20px;")
                self.produtos_layout.addWidget(info_label)
            else:
                for produto in produtos:
                    produto_widget = ProdutoItem(produto, modo='editar')
                    produto_widget.editar_clicado.connect(self.editar_produto)
                    self.produtos_layout.addWidget(produto_widget)

                    linha = QFrame()
                    linha.setFrameShape(QFrame.Shape.HLine)
                    linha.setFrameShadow(QFrame.Shadow.Sunken)
                    self.produtos_layout.addWidget(linha)
        else:
            erro_label = QLabel("Erro ao carregar produtos. Tente novamente.")
            erro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            erro_label.setStyleSheet("font-size: 14px; color: red; padding: 20px;")
            self.produtos_layout.addWidget(erro_label)
    
    def editar_loja(self):
        """Abre diálogo para editar informações da loja"""
        dialog = JanelaCriarLoja(self.cliente, self.loja_dados)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            resposta = self.cliente.obter_loja()
            if resposta and resposta.get('status') == 'sucesso':
                self.loja_dados = resposta.get('loja')
                self.setWindowTitle(f"Minha Loja - {self.loja_dados['nome_loja']}")
                self.close()
                self.__init__(self.cliente, self.loja_dados)
    
    def adicionar_produto(self):
        """Abre diálogo para adicionar novo produto"""
        dialog = JanelaCriarProduto(self.cliente)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_produtos()
    
    def editar_produto(self, produto):
        """Abre diálogo para editar um produto existente"""
        dialog = JanelaCriarProduto(self.cliente, produto)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_produtos()
    
    def ver_historico(self):
        """Abre janela com histórico de vendas"""
        dialog = JanelaHistoricoVendas(self.cliente)
        dialog.exec()

class JanelaHistoricoCompras(QDialog):
    """Janela para exibir histórico de compras do usuário"""
    def __init__(self, cliente):
        super().__init__()
        self.cliente = cliente
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Histórico de Compras")
        self.setFixedSize(800, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e2b2b;
                color: #e2c8a0;
            }
            QPushButton {
                background-color: #e2c8a0;
                color: #333333;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0b68e;
            }
            QLineEdit {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QComboBox {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QScrollArea {
                border: 1px solid #152121;
                border-radius: 5px;
            }
            QLabel {
                color: #e2c8a0;
            }
            QFrame {
                background-color: #1e2b2b;
            }
        """)

        layout = QVBoxLayout()

        titulo = QLabel("Histórico de Compras")
        titulo.setFont(QFont(FONTE_PRINCIPAL, 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        self.listar_compras(layout)

        fechar_btn = QPushButton("Fechar")
        fechar_btn.clicked.connect(self.accept)
        layout.addWidget(fechar_btn)

        self.setLayout(layout)

    def listar_compras(self, layout):
        resposta = self.cliente.historico_compras()
        if resposta and resposta.get('status') == 'sucesso':
            compras = resposta.get('compras', [])
            if not compras:
                info_label = QLabel("Você ainda não realizou nenhuma compra.")
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                info_label.setStyleSheet("font-size: 14px; padding: 20px;")
                layout.addWidget(info_label)
            else:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll_widget = QWidget()
                compras_layout = QVBoxLayout(scroll_widget)

                for compra in compras:
                    item_widget = self.criar_item_transacao(compra, tipo='compra')
                    compras_layout.addWidget(item_widget)

                    linha = QFrame()
                    linha.setFrameShape(QFrame.Shape.HLine)
                    linha.setFrameShadow(QFrame.Shadow.Sunken)
                    compras_layout.addWidget(linha)

                scroll.setWidget(scroll_widget)
                layout.addWidget(scroll)
        else:
            erro_label = QLabel("Erro ao carregar histórico de compras.")
            erro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            erro_label.setStyleSheet("font-size: 14px; color: red; padding: 20px;")
            layout.addWidget(erro_label)

    def criar_item_transacao(self, transacao, tipo):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)

        produto = transacao.get('produto', 'Produto desconhecido')
        valor = transacao.get('valor', 0.0)
        data = transacao.get('data', 'Data não informada')
        usuario = transacao.get('usuario', 'Desconhecido')

        descricao = f"Você comprou '{produto}' de {usuario} por {valor:.2f} galeões em {data}."
        label = QLabel(descricao)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 13px;")

        texto_layout = QVBoxLayout()
        texto_layout.addWidget(label)
        layout.addLayout(texto_layout)

        return widget


class JanelaHistoricoVendas(QDialog):
    """Janela para exibir histórico de vendas do usuário (loja)"""
    def __init__(self, cliente):
        super().__init__()
        self.cliente = cliente
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Histórico de Vendas")
        self.setFixedSize(800, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e2b2b;
                color: #e2c8a0;
            }
            QPushButton {
                background-color: #e2c8a0;
                color: #333333;
                border-radius: 5px;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d0b68e;
            }
            QLineEdit {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QComboBox {
                background-color: white;
                color: #333333;
                border-radius: 10px;
                padding: 5px;
            }
            QScrollArea {
                border: 1px solid #152121;
                border-radius: 5px;
            }
            QLabel {
                color: #e2c8a0;
            }
            QFrame {
                background-color: #1e2b2b;
            }
        """)

        layout = QVBoxLayout()

        titulo = QLabel("Histórico de Vendas")
        titulo.setFont(QFont(FONTE_PRINCIPAL, 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        self.listar_vendas(layout)

        fechar_btn = QPushButton("Fechar")
        fechar_btn.clicked.connect(self.accept)
        layout.addWidget(fechar_btn)

        self.setLayout(layout)

    def listar_vendas(self, layout):
        resposta = self.cliente.historico_vendas()
        if resposta and resposta.get('status') == 'sucesso':
            vendas = resposta.get('vendas', [])
            if not vendas:
                info_label = QLabel("Você ainda não realizou nenhuma venda.")
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                info_label.setStyleSheet("font-size: 14px; padding: 20px;")
                layout.addWidget(info_label)
            else:
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll_widget = QWidget()
                vendas_layout = QVBoxLayout(scroll_widget)

                for venda in vendas:
                    item_widget = self.criar_item_transacao(venda, tipo='venda')
                    vendas_layout.addWidget(item_widget)

                    linha = QFrame()
                    linha.setFrameShape(QFrame.Shape.HLine)
                    linha.setFrameShadow(QFrame.Shadow.Sunken)
                    vendas_layout.addWidget(linha)

                scroll.setWidget(scroll_widget)
                layout.addWidget(scroll)
        else:
            erro_label = QLabel("Erro ao carregar histórico de vendas.")
            erro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            erro_label.setStyleSheet("font-size: 14px; color: red; padding: 20px;")
            layout.addWidget(erro_label)

    def criar_item_transacao(self, transacao, tipo):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)

        produto = transacao.get('produto', 'Produto desconhecido')
        valor = transacao.get('valor', 0.0)
        data = transacao.get('data', 'Data não informada')
        usuario = transacao.get('usuario', 'Desconhecido')

        descricao = f"Você vendeu '{produto}' para {usuario} por {valor:.2f} galeões em {data}."
        label = QLabel(descricao)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 13px;")

        texto_layout = QVBoxLayout()
        texto_layout.addWidget(label)
        layout.addLayout(texto_layout)

        return widget
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela_login = JanelaLogin() 
    sys.exit(app.exec())

    