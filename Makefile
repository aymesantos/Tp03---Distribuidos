# Makefile para gerenciar o projeto

# Variáveis
PYTHON = python3
MAIN_SCRIPT = main.py

# Diretórios do projeto (serão inferidos automaticamente pelo script principal)
# Variáveis para comando de limpeza
PIDS = $(shell pgrep -f "python3 (servidor_dados.py|servidor.py|clienteGUI.py)")

# Comando padrão ao executar apenas 'make'
.PHONY: all
all: run

# Iniciar todos os serviços
.PHONY: run
run:
	@echo "Iniciando todos os serviços..."
	@$(PYTHON) $(MAIN_SCRIPT)
	@echo "Serviços iniciados com sucesso!"

# Limpar processos em segundo plano
.PHONY: stop
stop:
	@echo "Parando todos os serviços..."
	@-pkill -f "python3 servidor_dados.py" 2>/dev/null || true
	@-pkill -f "python3 servidor.py" 2>/dev/null || true
	@-pkill -f "python3 clienteGUI.py" 2>/dev/null || true
	@echo "Todos os serviços foram encerrados."

# Reiniciar todos os serviços
.PHONY: restart
restart: stop run

# Status dos serviços
.PHONY: status
status:
	@echo "Verificando status dos serviços..."
	@if pgrep -f "python3 servidor_dados.py" > /dev/null; then \
		echo "Servidor de dados: ATIVO"; \
	else \
		echo "Servidor de dados: INATIVO"; \
	fi
	@if pgrep -f "python3 servidor.py" > /dev/null; then \
		echo "Servidor principal: ATIVO"; \
	else \
		echo "Servidor principal: INATIVO"; \
	fi
	@if pgrep -f "python3 clienteGUI.py" > /dev/null; then \
		echo "Cliente GUI: ATIVO"; \
	else \
		echo "Cliente GUI: INATIVO"; \
	fi

# Ajuda
.PHONY: help
help:
	@echo "Comandos disponíveis:"
	@echo "  make run      - Inicia todos os serviços"
	@echo "  make stop     - Para todos os serviços"
	@echo "  make restart  - Reinicia todos os serviços"
	@echo "  make status   - Verifica o status dos serviços"
	@echo "  make help     - Mostra esta mensagem de ajuda"