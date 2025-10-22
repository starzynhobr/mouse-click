"""
Script de teste para verificar se todos os módulos estão funcionando
"""

print("=" * 50)
print("Testando componentes do AutoClicker Pro...")
print("=" * 50)

print("\n1. Testando importações...")
try:
    import pynput
    print("   ✓ pynput")
except ImportError as e:
    print(f"   ✗ pynput: {e}")

try:
    import customtkinter
    print("   ✓ customtkinter")
except ImportError as e:
    print(f"   ✗ customtkinter: {e}")

try:
    from PIL import Image
    print("   ✓ pillow (PIL)")
except ImportError as e:
    print(f"   ✗ pillow: {e}")

try:
    import pystray
    print("   ✓ pystray")
except ImportError as e:
    print(f"   ✗ pystray: {e}")

print("\n2. Testando módulo auto_clicker...")
try:
    from auto_clicker import AutoClicker
    print("   ✓ AutoClicker importado com sucesso")

    # Testa criação do objeto
    clicker = AutoClicker(cps=20)
    print("   ✓ AutoClicker instanciado com sucesso")
    print(f"   - CPS: {clicker.cps}")
    print(f"   - Intervalo: {clicker.click_interval:.4f}s")
except Exception as e:
    print(f"   ✗ Erro: {e}")

print("\n3. Testando GUI...")
try:
    from gui import AutoClickerGUI
    print("   ✓ AutoClickerGUI importado com sucesso")
except Exception as e:
    print(f"   ✗ Erro: {e}")

print("\n" + "=" * 50)
print("Teste concluído!")
print("=" * 50)
print("\nSe todos os testes passaram, você pode executar:")
print("  python gui.py")
print("\nOu clique duas vezes em: run.bat")
print("=" * 50)
