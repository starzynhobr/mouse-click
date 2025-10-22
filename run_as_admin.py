"""
Script para executar GUI como administrador
"""
import ctypes
import sys
import os
import subprocess

def is_admin():
    """Verifica se o script está rodando como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gui_script = os.path.join(script_dir, "gui.py")

    if not is_admin():
        print("=" * 70)
        print("Solicitando privilégios de administrador...")
        print("Aceite o UAC quando aparecer!")
        print("=" * 70)

        # Usa subprocess com runas via shell
        try:
            # Cria um comando PowerShell que executa como admin
            cmd = f'Start-Process python -ArgumentList \\"\\"{gui_script}\\"\\\" -Verb RunAs -WorkingDirectory \\"{script_dir}\\"'
            subprocess.run(['powershell', '-Command', cmd], check=True)
        except Exception as e:
            print(f"Erro ao executar como admin: {e}")
            input("Pressione Enter para sair...")
    else:
        # Já é admin, importa e executa a GUI
        print("=" * 70)
        print("✓ Executando como Administrador...")
        print("=" * 70)
        os.chdir(script_dir)
        exec(open(gui_script).read())
