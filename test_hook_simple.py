"""
Teste simples e direto do hook de mouse
Execute como administrador!
"""
import ctypes
import ctypes.wintypes as wintypes
import sys

# Verifica se é admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("❌ NÃO está rodando como administrador!")
    print("Execute: python run_as_admin.py")
    input("Pressione Enter para sair...")
    sys.exit(1)

print("✓ Rodando como Administrador")
print("")

# Setup
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WM_MBUTTONDOWN = 0x0207
LLMHF_INJECTED = 0x00000001

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]

LRESULT = ctypes.c_ssize_t
LowLevelMouseProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# Contador de eventos
event_count = 0

@LowLevelMouseProc
def mouse_callback(nCode, wParam, lParam):
    global event_count

    if nCode == 0:
        ms = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        injected = bool(ms.flags & LLMHF_INJECTED)

        if not injected:
            event_count += 1
            event_names = {
                0x0201: "LEFT_DOWN",
                0x0202: "LEFT_UP",
                0x0204: "RIGHT_DOWN",
                0x0205: "RIGHT_UP",
                0x0207: "MIDDLE_DOWN",
                0x0208: "MIDDLE_UP"
            }
            event_name = event_names.get(wParam, f"UNKNOWN({hex(wParam)})")
            print(f"[{event_count}] Evento detectado: {event_name}")

            if wParam == WM_MBUTTONDOWN:
                print("🎯 SCROLL CLICK! Hook está funcionando!")

    return user32.CallNextHookEx(None, nCode, wParam, lParam)

# Instala o hook
print("Instalando hook...")
WH_MOUSE_LL = 14

hook_id = user32.SetWindowsHookExW(
    WH_MOUSE_LL,
    mouse_callback,
    None,  # NULL para hooks globais
    0
)

if not hook_id:
    error = ctypes.get_last_error()
    print(f"❌ ERRO ao instalar hook! Código: {error}")
    print("")
    print("Possíveis causas:")
    print("1. Antivírus bloqueando")
    print("2. Outro programa conflitando")
    print("3. Windows bloqueando hooks")
    input("Pressione Enter para sair...")
    sys.exit(1)

print(f"✓ Hook instalado! ID: {hook_id}")
print("")
print("=" * 60)
print("TESTE: Clique com os botões do mouse")
print("- Especialmente o BOTÃO DO SCROLL (middle button)")
print("- Pressione Ctrl+C para sair")
print("=" * 60)
print("")

# Message loop
msg = wintypes.MSG()
try:
    while True:
        ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
        if ret == 0:
            break
        if ret == -1:
            print("Erro no message loop")
            break
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
except KeyboardInterrupt:
    print("")
    print("Encerrando...")

# Cleanup
user32.UnhookWindowsHookEx(hook_id)
print(f"Hook removido. Total de eventos detectados: {event_count}")
