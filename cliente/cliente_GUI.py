import sys
from PyQt6.QtWidgets import QApplication, QWidget,  QScrollArea, QFrame, QDialog, QVBoxLayout,QMenu, QLabel,QTextEdit,QSpinBox, QLineEdit,QListWidget,QStackedWidget, QPushButton,QHBoxLayout, QMessageBox, QComboBox
from cliente import Cliente
import re # Importando o módulo re para expressões regulares
from PyQt6.QtGui import QPixmap, QPalette, QBrush,  QPainter, QFont
from PyQt6.QtCore import Qt


class JanelaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.adjustSize()
        self.cliente = Cliente()

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
        self.login_btn = QPushButton('', self)  # Sem texto, para combinar com a imagem
        self.login_btn.setGeometry(834, 446, 184, 63)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0);
                border: none;
            }
            QPushButton:hover {
                cursor: pointer;
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
                cursor: pointer;
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
                QMessageBox.information(self, 'Sucesso', 'Login realizado com sucesso!')
                self.ir_para_marketplace()
            elif resposta.get('erro') == 'senha_incorreta':
                QMessageBox.warning(self, 'Erro', 'Senha incorreta!')
            elif resposta.get('erro') == 'usuario_nao_encontrado':
                QMessageBox.warning(self, 'Erro', 'Usuário não encontrado!')
            else:
                QMessageBox.warning(self, 'Erro', 'Erro no login.')
        else:
            QMessageBox.warning(self, 'Erro', 'Erro de conexão com o servidor.')

    def ir_para_cadastro(self):
        self.close()
        self.janela_cadastro = JanelaCadastro(self.cliente)
        self.janela_cadastro.show()

    def ir_para_marketplace(self):
        self.close()
        self.janela_marketplace = JanelaMarketplace(self.cliente)
        self.janela_marketplace.show()

#### Tela de Cadastro
class JanelaCadastro(QWidget):
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
                cursor: pointer;
            }
        """)
        self.cadastrar_btn.clicked.connect(self.realizar_cadastro)

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

        # Verificações locais
        if not all([nome, email, senha]):
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos!')
            return
        
        if casa == "Selecionar casa" or tipo_bruxo == "Selecionar tipo de bruxo":
            QMessageBox.warning(self, 'Erro', 'Selecione uma casa e o tipo de bruxo.')
            return

        if not re.match(r'^[A-Za-z0-9 ]{4,20}$', nome):
            QMessageBox.warning(self, 'Erro', 'Nome deve ter entre 4 e 20 caracteres e conter apenas letras, números e espaços.')
            return

        if len(senha) < 8:
            QMessageBox.warning(self, 'Erro', 'A senha deve ter no mínimo 8 caracteres.')
            return

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            QMessageBox.warning(self, 'Erro', 'Email inválido.')
            return

        resposta = self.cliente.cadastro(nome, casa, email, senha, tipo_bruxo)

        if resposta:
            if resposta.get('status') == 'sucesso':
                QMessageBox.information(self, 'Sucesso', 'Cadastro realizado com sucesso!')
                self.close()
                self.janela_login = JanelaLogin()
                self.janela_login.show()
            elif resposta.get('erro') == 'email_ja_cadastrado':
                QMessageBox.warning(self, 'Erro', 'Email já cadastrado.')
            else:
                QMessageBox.warning(self, 'Erro', 'Erro no cadastro, tente novamente!')
        else:
            QMessageBox.warning(self, 'Erro', 'Erro de conexão com o servidor.')

            
class JanelaMarketplace(QWidget):
    """Tela principal do marketplace com navegação entre seções"""
    def __init__(self, cliente):
        super().__init__()
        self.cliente = cliente
        self.carrinho = []  # Lista para armazenar produtos no carrinho
        self.initUI()
        self.carregar_produtos()
        
    def initUI(self):
        self.setWindowTitle('BecoDiagonal - Marketplace')
        self.setFixedSize(1366, 768)
        
        # Definir o estilo global para aplicação
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
        logo_pixmap = QPixmap("imagens/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(150, 50, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            print("Imagem não carregada.")
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
        
        # Área de conteúdo principal com produtos
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.produtos_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        
        main_layout.addWidget(self.scroll_area)
        
        self.setLayout(main_layout)
        
    def carregar_produtos(self, categoria=None, termo_busca=None):
        """Carrega os produtos do servidor com filtros opcionais"""
        # Limpar layout de produtos
        while self.produtos_layout.count():
            item = self.produtos_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Buscar produtos no servidor
        resposta = self.cliente.listar_produtos(filtros={'categoria': categoria, 'termo_busca': termo_busca})
        
        if resposta and resposta.get('status') == 'sucesso':
            produtos = resposta.get('produtos', [])
            
            if not produtos:
                info_label = QLabel("Nenhum produto encontrado.")
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                info_label.setStyleSheet("font-size: 16px; padding: 20px; color: #e2c8a0;")
                self.produtos_layout.addWidget(info_label)
            else:
                for produto in produtos:
                    produto_widget = ProdutoItem(produto, modo='comprar', tema_escuro=True)
                    produto_widget.comprar_clicado.connect(self.adicionar_ao_carrinho)
                    self.produtos_layout.addWidget(produto_widget)
                    
                    # Adicionar linha separadora
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
        # Verificar se o produto já está no carrinho
        for item in self.carrinho:
            if item['id'] == produto['id']:
                QMessageBox.information(self, "Aviso", "Este produto já está no seu carrinho.")
                return
        
        # Adicionar ao carrinho
        self.carrinho.append(produto)
        QMessageBox.information(self, "Sucesso", f"'{produto['titulo']}' adicionado ao carrinho!")
        
        # Atualizar contador do botão de carrinho
        self.carrinho_btn.setText(f"Carrinho ({len(self.carrinho)})")
    
    def abrir_carrinho(self):
        """Abre a janela do carrinho de compras"""
        dialog = JanelaCarrinho(self.cliente, self.carrinho)
        # Aplicar o tema escuro na janela de carrinho
        dialog.setStyleSheet(self.styleSheet())
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            # Carrinho foi modificado ou compra foi finalizada
            self.carrinho = dialog.carrinho
            self.carrinho_btn.setText(f"Carrinho ({len(self.carrinho)})")
            
            # Se compra foi finalizada
            if dialog.compra_finalizada:
                # Recarregar produtos para refletir mudanças
                self.carregar_produtos()
    
    def abrir_perfil(self):
        """Abre a janela de edição do perfil do usuário"""
        dialog = JanelaPerfilUsuario(self.cliente)
        # Aplicar o tema escuro na janela de perfil
        dialog.setStyleSheet(self.styleSheet())
        dialog.exec()
    
    def abrir_minha_loja(self):
        """Abre a janela da loja do usuário"""
        resposta = self.cliente.obter_minha_loja()
        
        if resposta and resposta.get('status') == 'sucesso':
            # Usuário já tem uma loja
            loja_data = resposta.get('loja')
            janela_loja = JanelaMinhaLoja(self.cliente, loja_data)
            # Aplicar o tema escuro na janela da loja
            janela_loja.setStyleSheet(self.styleSheet())
            janela_loja.exec()
        elif resposta and resposta.get('erro') == 'loja_nao_encontrada':
            # Usuário não tem loja, perguntar se deseja criar
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Criar Loja")
            msg_box.setText("Você ainda não possui uma loja. Deseja criar agora?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e2b2b;
                }
                QLabel {
                    color: #e2c8a0;
                }
                QPushButton {
                    background-color: #e2c8a0;
                    color: #333333;
                    border-radius: 5px;
                    padding: 5px;
                    min-width: 80px;
                }
            """)
            reply = msg_box.exec()
            
            if reply == QMessageBox.StandardButton.Yes:
                dialog = JanelaCriarLoja(self.cliente)
                # Aplicar o tema escuro na janela de criação de loja
                dialog.setStyleSheet(self.styleSheet())
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    # Loja criada, abrir a janela da loja
                    self.abrir_minha_loja()
        else:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Erro")
            msg_box.setText("Erro ao acessar informações da loja.")
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e2b2b;
                }
                QLabel {
                    color: #ff6b6b;
                }
                QPushButton {
                    background-color: #e2c8a0;
                    color: #333333;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
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
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1e2b2b;
                }
                QLabel {
                    color: #ff6b6b;
                }
                QPushButton {
                    background-color: #e2c8a0;
                    color: #333333;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            msg_box.exec()


 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela_login = JanelaLogin()  # A primeira tela que será aberta é o login
    sys.exit(app.exec())


