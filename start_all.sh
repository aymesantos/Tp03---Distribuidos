#!/bin/bash

# Caminho absoluto do projeto
PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"

# Função para abrir terminal novo
open_terminal() {
    CMD="$1"
    TITLE="$2"
    if command -v xterm &> /dev/null; then
        xterm -T "$TITLE" -e "bash -c '$CMD; exec bash'" &
    elif command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$TITLE" -- bash -c "$CMD; exec bash" &
    elif command -v konsole &> /dev/null; then
        konsole --new-tab -p tabtitle="$TITLE" -e bash -c "$CMD; exec bash" &
    else
        echo "Nenhum terminal gráfico encontrado. Execute manualmente: $CMD"
    fi
}

# Servidor de dados
open_terminal "cd '$PROJ_DIR/Dados' && python3 servidor_dados.py" "Servidor Dados"

# Servidor mock
open_terminal "cd '$PROJ_DIR/servidor' && python3 servidor.py" "Servidor Mock"

# Cliente GUI
open_terminal "cd '$PROJ_DIR/cliente' && python3 clienteGUI.py" "Cliente GUI"

# Mensagem final
sleep 1
echo "Todos os servidores foram abertos em terminais separados."
echo "Para encerrar, feche as janelas dos terminais ou mate os processos manualmente." 