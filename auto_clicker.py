"""
Auto-Clicker usando Windows Low-Level Mouse Hook (WH_MOUSE_LL)
Solução que distingue cliques físicos de cliques programáticos usando LLMHF_INJECTED
"""
from pynput.keyboard import GlobalHotKeys
import ctypes
import ctypes.wintypes as wintypes
import os
import threading
import time
import sys

# Verbose logging is off by default: the hook callback runs on every mouse event,
# and printing there costs latency (and goes nowhere in a windowed build).
DEBUG = os.environ.get("STZ_CLICKER_DEBUG") == "1"


def log(message):
    if DEBUG:
        print(message)

# Windows API
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Mensagens do mouse (Low-level)
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP   = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP   = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP   = 0x0208

# Flag para detectar evento injetado
LLMHF_INJECTED = 0x00000001

# Estrutura MSLLHOOKSTRUCT
class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]

# Tipo para HookProc (LRESULT é LONG_PTR - pointer-sized integer)
LRESULT = ctypes.c_ssize_t  # Funciona em 32 e 64 bit
LowLevelMouseProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

# INPUT structures para SendInput
PUL = ctypes.POINTER(wintypes.ULONG)

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", PUL)
    ]

class INPUT(ctypes.Structure):
    class _I(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _anonymous_ = ("i",)
    _fields_ = [("type", wintypes.DWORD), ("i", _I)]

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP   = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP   = 0x0010

SendInput = user32.SendInput
SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
SendInput.restype  = wintypes.UINT

# Variável global para armazenar instância do AutoClicker
_auto_clicker_instance = None

# Callback global do hook
@LowLevelMouseProc
def _global_mouse_hook(nCode, wParam, lParam):
    """Hook callback global - delega para a instância do AutoClicker"""
    if _auto_clicker_instance:
        return _auto_clicker_instance._mouse_hook_callback(nCode, wParam, lParam)
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

class AutoClicker:
    def __init__(
        self,
        cps=20,
        enable_right_click=False,
        hotkey='<ctrl>+<shift>+a',
        burst_mode=False,
        burst_clicks=3,
        status_callback=None
    ):
        """
        Inicializa o auto-clicker com hook de baixo nível

        Args:
            cps: Clicks por segundo
            enable_right_click: Habilita auto-click no botão direito
            hotkey: Tecla de atalho (não implementado nesta versão)
            status_callback: Função callback para notificar mudanças de estado
        """
        self.cps = cps
        self.click_interval = 1.0 / cps
        self.enable_right_click = enable_right_click
        self.burst_mode = burst_mode
        self.burst_clicks = max(1, int(burst_clicks))
        self.status_callback = status_callback

        # Estado
        self.auto_click_enabled = False
        self.left_holding = False
        self.right_holding = False
        self.running = True
        self.left_burst_active = False
        self.right_burst_active = False
        self.left_burst_lock = threading.Lock()
        self.right_burst_lock = threading.Lock()

        # Hook
        self.hook_id = None
        self.hook_proc = None

        # Thread do clicker
        self.clicker_thread = None

        # Thread para message loop do hook
        self.hook_thread = None
        self.hook_thread_id = None

        self.hotkey = hotkey
        self.hotkey_listener = None

    def set_cps(self, cps):
        """Atualiza os cliques por segundo"""
        self.cps = cps
        self.click_interval = 1.0 / cps

    def set_right_click(self, enabled):
        """Habilita/desabilita auto-click no botão direito"""
        self.enable_right_click = enabled

    def set_burst_mode(self, enabled):
        """Habilita/desabilita o modo rajada"""
        self.burst_mode = enabled

    def set_burst_clicks(self, clicks):
        """Atualiza a quantidade de cliques por rajada"""
        self.burst_clicks = max(1, int(clicks))

    def set_hotkey(self, hotkey):
        """Define e registra nova tecla de atalho"""
        log(f"[HOTKEY] Tentando registrar novo atalho: {hotkey}")
        self.hotkey = hotkey

        # Para o listener antigo, se existir
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception as e:
                log(f"[DEBUG] Erro ao parar listener antigo: {e}")
            self.hotkey_listener = None

        # Tenta criar o novo listener
        if not self.hotkey:
            log("[HOTKEY] Atalho vazio, listener não iniciado.")
            return

        try:
            hotkey_map = {
                self.hotkey: self.toggle_auto_click
            }
            self.hotkey_listener = GlobalHotKeys(hotkey_map)
            self.hotkey_listener.start()
            log(f"[HOTKEY] ✓ Atalho {hotkey} registrado com sucesso.")
        except Exception as e:
            print(f"[ERRO] Falha ao registrar atalho '{hotkey}': {e}")
            print("[ERRO] Verifique se o formato está correto (ex: <ctrl>+<shift>+a)")
            self.hotkey_listener = None

    def toggle_auto_click(self):
        """Alterna entre ativar/desativar o modo auto-click"""
        self.auto_click_enabled = not self.auto_click_enabled
        status = 'ATIVADO' if self.auto_click_enabled else 'DESATIVADO'
        log(f"[TOGGLE] Auto-click {status}")

        if self.status_callback:
            self.status_callback(self.auto_click_enabled)

    def click_left(self):
        """Gera um clique esquerdo via SendInput"""
        down = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, None))
        up = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, None))
        arr = (INPUT * 2)(down, up)
        SendInput(2, arr, ctypes.sizeof(INPUT))

    def click_right(self):
        """Gera um clique direito via SendInput"""
        down = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, None))
        up = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, None))
        arr = (INPUT * 2)(down, up)
        SendInput(2, arr, ctypes.sizeof(INPUT))

    def trigger_burst(self, button):
        """Dispara uma rajada de cliques sem bloquear o hook do mouse"""
        if button == "left":
            if self.left_burst_active:
                return
            threading.Thread(target=self._execute_burst, args=(button,), daemon=True).start()
        elif button == "right":
            if self.right_burst_active:
                return
            threading.Thread(target=self._execute_burst, args=(button,), daemon=True).start()

    def _execute_burst(self, button):
        """Executa a quantidade configurada de cliques o mais rápido possível"""
        if button == "left":
            lock = self.left_burst_lock
            click_fn = self.click_left
            active_attr = "left_burst_active"
        else:
            lock = self.right_burst_lock
            click_fn = self.click_right
            active_attr = "right_burst_active"

        with lock:
            setattr(self, active_attr, True)
            try:
                for _ in range(self.burst_clicks):
                    if not self.running or not self.auto_click_enabled:
                        break
                    click_fn()
            finally:
                setattr(self, active_attr, False)

    def clicker_loop(self):
        """Thread que dispara os cliques enquanto o botão está sendo segurado"""
        click_count = 0

        while self.running:
            # Botão esquerdo
            if self.auto_click_enabled and not self.burst_mode and self.left_holding:
                self.click_left()
                click_count += 1

                if DEBUG and click_count % 10 == 0:
                    log(f"[DEBUG] Cliques esquerdos: {click_count}")

                time.sleep(self.click_interval)

            # Botão direito (se habilitado)
            elif self.enable_right_click and self.auto_click_enabled and not self.burst_mode and self.right_holding:
                self.click_right()
                click_count += 1

                if DEBUG and click_count % 10 == 0:
                    log(f"[DEBUG] Cliques direitos: {click_count}")

                time.sleep(self.click_interval)
            else:
                time.sleep(0.01)

    def _mouse_hook_callback(self, nCode, wParam, lParam):
        """Hook callback interno - processa apenas eventos físicos"""
        if nCode == 0:
            ms = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            injected = bool(ms.flags & LLMHF_INJECTED)

            # Ignora eventos injetados (nossos cliques programáticos)
            if not injected:
                # Botão do meio (scroll) - toggle auto-click
                if wParam == WM_MBUTTONDOWN:
                    log("[DEBUG] SCROLL CLICK detectado! Toggling...")
                    self.toggle_auto_click()

                # Botão esquerdo
                elif wParam == WM_LBUTTONDOWN:
                    self.left_holding = True
                    if self.auto_click_enabled and self.burst_mode:
                        self.trigger_burst("left")
                elif wParam == WM_LBUTTONUP:
                    self.left_holding = False

                # Botão direito
                elif wParam == WM_RBUTTONDOWN:
                    self.right_holding = True
                    if self.enable_right_click and self.auto_click_enabled and self.burst_mode:
                        self.trigger_burst("right")
                elif wParam == WM_RBUTTONUP:
                    self.right_holding = False

        # Chama próximo hook
        return user32.CallNextHookEx(None, nCode, wParam, lParam)

    def install_hook(self):
        """Instala o hook e roda o message loop"""
        global _auto_clicker_instance
        _auto_clicker_instance = self

        self.hook_thread_id = kernel32.GetCurrentThreadId()

        WH_MOUSE_LL = 14

        log("[INFO] Tentando instalar hook...")
        log(f"[INFO] Thread ID: {self.hook_thread_id}")

        # Para hooks globais (WH_MOUSE_LL), passamos NULL como hMod
        # Isso funciona melhor do que GetModuleHandleW
        self.hook_id = user32.SetWindowsHookExW(
            WH_MOUSE_LL,
            _global_mouse_hook,
            None,  # NULL para hooks globais
            0      # dwThreadId = 0 (todos os threads)
        )

        if not self.hook_id:
            # Pega o código de erro do Windows
            error_code = ctypes.get_last_error()
            print(f"[ERRO] Falha ao instalar hook!")
            print(f"[ERRO] Código de erro: {error_code}")
            print(f"[ERRO] Possíveis causas:")
            print(f"  - Falta de privilégios de administrador")
            print(f"  - Antivírus bloqueando")
            print(f"  - Outro programa usando hook global")
            return

        log("[INFO] ✓ Hook de mouse instalado com sucesso!")
        log(f"[INFO] ✓ Hook ID: {self.hook_id}")
        log("[INFO] ✓ Aguardando eventos de mouse...")

        # Message loop necessário para manter o hook vivo
        msg = wintypes.MSG()
        while self.running:
            ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if ret == 0:  # WM_QUIT
                break
            if ret == -1:
                print("[ERRO] Erro no GetMessage")
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        # Cleanup
        if self.hook_id:
            user32.UnhookWindowsHookEx(self.hook_id)
            log("[INFO] Hook removido")

    def is_admin(self):
        """Verifica se está rodando como administrador"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def start(self):
        """Inicia o auto-clicker"""
        # Verifica privilégios
        if not self.is_admin():
            print("[AVISO] Programa NAO esta rodando como Administrador.")
            print("[AVISO] O hook de mouse pode falhar sem privilegios elevados.")
        else:
            log("[INFO] Executando como Administrador")

        self.set_hotkey(self.hotkey)

        # Inicia thread do clicker
        self.clicker_thread = threading.Thread(target=self.clicker_loop, daemon=True)
        self.clicker_thread.start()

        # Inicia hook em thread separada
        self.hook_thread = threading.Thread(target=self.install_hook, daemon=False)
        self.hook_thread.start()

    def stop(self):
        """Para o auto-clicker"""
        global _auto_clicker_instance

        self.running = False
        _auto_clicker_instance = None

        # Para o listener de atalho
        if self.hotkey_listener: # <-- ADICIONE ESTA LINHA
            self.hotkey_listener.stop()

        # Envia WM_QUIT para sair do message loop
        if self.hook_thread and self.hook_thread.is_alive():
            user32.PostThreadMessageW(
                self.hook_thread_id,
                0x0012,  # WM_QUIT
                0,
                0
            )
            self.hook_thread.join(timeout=1.0)

if __name__ == "__main__":
    if sys.platform != "win32":
        print("Este script é compatível apenas com Windows.")
        sys.exit(1)

    def status_changed(enabled):
        print(f"[CALLBACK] Status mudou: {'ATIVADO' if enabled else 'DESATIVADO'}")

    print("=" * 60)
    print("STZ Clicker - Versão com Hook de Baixo Nível")
    print("=" * 60)
    print("Instruções:")
    print("1. Clique no BOTÃO DO SCROLL (middle button) para ATIVAR/DESATIVAR")
    print("2. Quando ativado, SEGURE o botão esquerdo para auto-click")
    print("3. SOLTE o botão para parar")
    print("4. Ctrl+C para sair")
    log("=" * 60)

    clicker = AutoClicker(cps=20, status_callback=status_changed)
    clicker.start()

    try:
        # Mantém programa rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Encerrando...")
        clicker.stop()
