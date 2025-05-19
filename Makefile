PYTHON = python3
MAIN_SCRIPT = main.py

PIDS = $(shell pgrep -f "python3 (servidor_dados.py|servidor.py|clienteGUI.py)")

.PHONY: all
all: run

.PHONY: run
run:
	@echo "Iniciando todos os serviços..."
	@$(PYTHON) $(MAIN_SCRIPT)
	@echo "Serviços iniciados com sucesso!"

.PHONY: stop
stop:
	@echo "Parando todos os serviços..."
	@-pkill -f "python3 servidor_dados.py" 2>/dev/null || true
	@-pkill -f "python3 servidor.py" 2>/dev/null || true
	@-pkill -f "python3 clienteGUI.py" 2>/dev/null || true
	@echo "Todos os serviços foram encerrados."

.PHONY: restart
restart: stop run

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

.PHONY: help
help:
	@echo "Comandos disponíveis:"
	@echo "  make run      - Inicia todos os serviços"
	@echo "  make stop     - Para todos os serviços"
	@echo "  make restart  - Reinicia todos os serviços"
	@echo "  make status   - Verifica o status dos serviços"
	@echo "  make help     - Mostra esta mensagem de ajuda"
