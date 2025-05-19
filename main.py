import subprocess
import os
import time

def run_background(command, cwd):
    # Inicia o processo em segundo plano no diretório especificado
    subprocess.Popen(command, cwd=cwd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    # Caminho absoluto do diretório do script
    proj_dir = os.path.dirname(os.path.abspath(__file__))

    # Caminhos dos diretórios
    dados_dir = os.path.join(proj_dir, "Dados")
    servidor_dir = os.path.join(proj_dir, "servidor")
    cliente_dir = os.path.join(proj_dir, "cliente")

    # Inicia os scripts em background
    run_background("python3 servidor_dados.py", dados_dir)
    run_background("python3 servidor.py", servidor_dir)
    run_background("python3 clienteGUI.py", cliente_dir)

    # Mensagem final
    time.sleep(1)
    print("Todos os servidores foram iniciados em background.")
    print("Para encerrar, finalize os processos manualmente (por PID ou killall).")

if __name__ == "__main__":
    main()
