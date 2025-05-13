from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import sys

def iniciar_interface():
    app = QApplication(sys.argv)
    janela = QWidget()
    janela.setWindowTitle("Servidor de Dados - BecoDiagonal")
    layout = QVBoxLayout()
    layout.addWidget(QLabel("Servidor de Dados está em execução..."))
    janela.setLayout(layout)
    janela.show()
    sys.exit(app.exec())
