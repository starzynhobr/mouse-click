"""Teste rápido do hook"""
import time
from auto_clicker_v2 import AutoClicker

print("Testando auto_clicker_v2...")
print("1. Clique no scroll para ativar")
print("2. Segure o botão esquerdo")
print("3. Aguarde 5 segundos...")

clicker = AutoClicker(cps=20)
clicker.start()

# Aguarda 15 segundos
time.sleep(15)

print("Encerrando teste...")
clicker.stop()
print("Teste finalizado")
