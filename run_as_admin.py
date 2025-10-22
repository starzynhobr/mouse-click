"""
Script para executar GUI como administrador
"""
import ctypes
import sys
import os

def is_admin():
    """Verifica se o script está rodando como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if not is_admin():
        print("Solicitando privilégios de administrador...")
        # Re-executa o script como administrador
        script = os.path.join(os.path.dirname(__file__), "gui.py")
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # Verb para executar como admin
            sys.executable,  # Python
            f'"{script}"',  # Arquivo a executar
            os.path.dirname(__file__),  # Working directory
            1  # SW_SHOWNORMAL
        )
    else:
        # Já é admin, importa e executa a GUI
        print("Executando como Administrador...")
        import gui
