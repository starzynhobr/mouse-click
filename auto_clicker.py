"""
Script de Auto-Clicker Customizado
- Core do auto-clicker com suporte para interface gráfica
"""

import threading
import time
import ctypes
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller
from pynput.keyboard import Key, KeyCode

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class AutoClicker:
    # Códigos de tecla virtual do Windows para GetAsyncKeyState
    VK_LBUTTON = 0x01  # Botão esquerdo do mouse
    VK_RBUTTON = 0x02  # Botão direito do mouse

    # Constantes para mouse_event
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010

    @staticmethod
    def is_button_pressed(button):
        """Verifica se um botão do mouse está pressionado usando Windows API"""
        if button == Button.left:
            vk_code = AutoClicker.VK_LBUTTON
        elif button == Button.right:
            vk_code = AutoClicker.VK_RBUTTON
        else:
            return False

        # GetAsyncKeyState retorna um short
        # Bit mais significativo (0x8000) indica se a tecla está pressionada
        state = ctypes.windll.user32.GetAsyncKeyState(vk_code)
        return (state & 0x8000) != 0

    @staticmethod
    def click_windows_api(button):
        """Faz um clique usando Windows API diretamente"""
        if button == Button.left:
            # Clique esquerdo: down + up
            ctypes.windll.user32.mouse_event(AutoClicker.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(AutoClicker.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        elif button == Button.right:
            # Clique direito: down + up
            ctypes.windll.user32.mouse_event(AutoClicker.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(AutoClicker.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def __init__(self, cps=20, enable_right_click=False, hotkey='<ctrl>+<shift>+a', status_callback=None):
        """
        Inicializa o auto-clicker

        Args:
            cps: Clicks por segundo (padrão: 20)
            enable_right_click: Habilita auto-click no botão direito também
            hotkey: Tecla de atalho para ativar/desativar
            status_callback: Função callback para notificar mudanças de estado
        """
        self.mouse_controller = Controller()
        self.cps = cps
        self.click_interval = 1.0 / cps
        self.enable_right_click = enable_right_click
        self.hotkey = hotkey
        self.status_callback = status_callback

        # Estado do auto-clicker
        self.auto_click_enabled = False
        self.clicking = False
        self.running = True

        # Controle de qual botão está sendo auto-clicado
        self.current_auto_button = None

        # Thread para os cliques
        self.click_thread = None

        # Listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        self.hotkey_listener = None

    def set_cps(self, cps):
        """Atualiza os cliques por segundo"""
        self.cps = cps
        self.click_interval = 1.0 / cps

    def set_right_click(self, enabled):
        """Habilita/desabilita auto-click no botão direito"""
        self.enable_right_click = enabled

    def set_hotkey(self, hotkey):
        """Define nova tecla de atalho"""
        self.hotkey = hotkey
        # Reinicia o listener de hotkey
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            self.start_hotkey_listener()

    def toggle_auto_click(self):
        """Alterna entre ativar/desativar o modo auto-click"""
        self.auto_click_enabled = not self.auto_click_enabled
        status = "ATIVADO" if self.auto_click_enabled else "DESATIVADO"
        print(f"[DEBUG] Auto-click {status}")

        # Notifica callback
        if self.status_callback:
            self.status_callback(self.auto_click_enabled)

        # Se desativar enquanto está clicando, para os cliques
        if not self.auto_click_enabled:
            self.clicking = False

    def perform_clicks(self, button):
        """Executa cliques contínuos enquanto o botão estiver pressionado"""
        click_count = 0
        print(f"[DEBUG] Iniciando cliques automáticos...")

        # Loop de cliques com verificação integrada
        while self.clicking and self.auto_click_enabled:
            # Faz o clique usando Windows API diretamente
            self.click_windows_api(button)
            click_count += 1

            if click_count % 10 == 0:
                print(f"[DEBUG] Cliques realizados: {click_count}")

            # Aguarda metade do intervalo
            time.sleep(self.click_interval / 2)

            # AGORA verifica o estado (sistema está estável entre cliques)
            is_pressed = self.is_button_pressed(button)

            if not is_pressed:
                print(f"[DEBUG] Botão SOLTO detectado - parando (após {click_count} cliques)")
                break

            # Aguarda a outra metade do intervalo antes do próximo clique
            time.sleep(self.click_interval / 2)

        print(f"[DEBUG] Total de cliques: {click_count}")

    def start_clicking(self, button):
        """Inicia a thread de cliques automáticos"""
        # Para qualquer clique anterior antes de iniciar novo
        self.stop_clicking()

        self.clicking = True

        # Inicia a thread de cliques (que agora também monitora o estado)
        self.click_thread = threading.Thread(target=self.perform_clicks, args=(button,), daemon=True)
        self.click_thread.start()

    def stop_clicking(self):
        """Para os cliques automáticos"""
        self.clicking = False

        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=0.3)

    def on_click(self, x, y, button, pressed):
        """Callback para eventos de clique do mouse"""
        # Botão do meio (scroll) - toggle auto-click (sempre processa)
        if button == Button.middle and pressed:
            self.toggle_auto_click()
            return

        # Durante auto-click, IGNORA TODOS os eventos (a thread de cliques cuida de tudo)
        if self.clicking:
            print(f"[DEBUG] Evento ignorado - auto-click ativo")
            return

        # Botão esquerdo - iniciar cliques automáticos (se modo ativado)
        if button == Button.left and self.auto_click_enabled and pressed:
            print(f"[DEBUG] Botão esquerdo PRESSIONADO (usuário)")
            self.current_auto_button = Button.left
            self.start_clicking(Button.left)
            return

        # Botão direito - iniciar cliques automáticos (se habilitado e modo ativado)
        if button == Button.right and self.enable_right_click and self.auto_click_enabled and pressed:
            print(f"[DEBUG] Botão direito PRESSIONADO (usuário)")
            self.current_auto_button = Button.right
            self.start_clicking(Button.right)
            return

    def on_hotkey_press(self):
        """Callback para o atalho de teclado"""
        self.toggle_auto_click()

    def start_hotkey_listener(self):
        """Inicia o listener de hotkey"""
        try:
            from pynput.keyboard import GlobalHotKeys

            hotkeys = {
                self.hotkey: self.on_hotkey_press
            }

            self.hotkey_listener = GlobalHotKeys(hotkeys)
            self.hotkey_listener.start()
        except Exception as e:
            print(f"Erro ao iniciar hotkey listener: {e}")

    def start(self):
        """Inicia o auto-clicker"""
        # Inicia os listeners
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

        # Inicia o listener de hotkey
        self.start_hotkey_listener()

    def stop(self):
        """Para o auto-clicker"""
        self.running = False
        self.stop_clicking()

        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.hotkey_listener:
            self.hotkey_listener.stop()

if __name__ == "__main__":
    # Modo console (sem UI)
    def status_changed(enabled):
        status = "ATIVADO" if enabled else "DESATIVADO"
        print(f"Auto-click {status}")

    print("=" * 50)
    print("Auto-Clicker (Modo Console)")
    print("=" * 50)
    print("Clique no BOTÃO DO SCROLL para ativar/desativar")
    print("Ctrl+Shift+A também ativa/desativa")
    print("Ctrl+C para sair")
    print("=" * 50)

    clicker = AutoClicker(cps=20, enable_right_click=False, status_callback=status_changed)
    clicker.start()

    try:
        while clicker.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        clicker.stop()
        print("Programa encerrado.")
