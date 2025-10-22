"""
Interface Gráfica Moderna para Auto-Clicker
Usando CustomTkinter para um design moderno e minimalista
"""

import customtkinter as ctk
import threading
from auto_clicker import AutoClicker
import sys
import pystray
from PIL import Image, ImageDraw
from pynput.keyboard import GlobalHotKeys
import json
import os

# Configurações do CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AutoClickerGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("AutoClicker Pro")
        self.window.geometry("380x520")
        self.window.resizable(False, False)

        # Configurações
        self.config_file = "config.json"
        self.config = self.load_config()

        # Auto-clicker
        self.clicker = None
        self.is_enabled = False
        self.hidden = False

        # System tray
        self.tray_icon = None

        # Cria a interface
        self.create_widgets()

        # Inicia o auto-clicker
        self.start_clicker()

        # Protocolo de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        """Carrega configurações do arquivo"""
        default_config = {
            "cps": 20,
            "enable_right_click": False,
            "hotkey": "<ctrl>+<shift>+a",
            "hide_on_minimize": False
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Erro ao carregar config: {e}")

        return default_config

    def save_config(self):
        """Salva configurações no arquivo"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")

    def create_widgets(self):
        """Cria todos os widgets da interface"""

        # Frame principal com padding
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ============= HEADER =============
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="AutoClicker Pro",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack()

        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Controle avançado de cliques automáticos",
            font=ctk.CTkFont(size=12),
            text_color="gray60"
        )
        subtitle_label.pack(pady=(5, 0))

        # ============= STATUS =============
        status_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        status_frame.pack(fill="x", pady=(0, 20))

        status_inner = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_inner.pack(padx=20, pady=15)

        self.status_indicator = ctk.CTkLabel(
            status_inner,
            text="●",
            font=ctk.CTkFont(size=40),
            text_color="#ef4444"
        )
        self.status_indicator.pack(side="left", padx=(0, 15))

        status_text_frame = ctk.CTkFrame(status_inner, fg_color="transparent")
        status_text_frame.pack(side="left")

        self.status_label = ctk.CTkLabel(
            status_text_frame,
            text="Desativado",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.status_label.pack(anchor="w")

        self.status_subtitle = ctk.CTkLabel(
            status_text_frame,
            text="Use scroll ou atalho para ativar",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.status_subtitle.pack(anchor="w", pady=(2, 0))

        # ============= CPS SLIDER =============
        cps_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        cps_frame.pack(fill="x", pady=(0, 15))

        cps_inner = ctk.CTkFrame(cps_frame, fg_color="transparent")
        cps_inner.pack(fill="x", padx=20, pady=15)

        cps_header = ctk.CTkFrame(cps_inner, fg_color="transparent")
        cps_header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            cps_header,
            text="Clicks por Segundo",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        self.cps_value_label = ctk.CTkLabel(
            cps_header,
            text=str(self.config["cps"]),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3b82f6"
        )
        self.cps_value_label.pack(side="right")

        self.cps_slider = ctk.CTkSlider(
            cps_inner,
            from_=1,
            to=50,
            number_of_steps=49,
            command=self.on_cps_change
        )
        self.cps_slider.set(self.config["cps"])
        self.cps_slider.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            cps_inner,
            text="Recomendado: 20 clicks/s",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        ).pack()

        # ============= OPÇÕES =============
        options_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        options_frame.pack(fill="x", pady=(0, 15))

        options_inner = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_inner.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            options_inner,
            text="Opções",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        # Right Click
        self.right_click_var = ctk.BooleanVar(value=self.config["enable_right_click"])
        right_click_switch = ctk.CTkSwitch(
            options_inner,
            text="Habilitar botão direito",
            variable=self.right_click_var,
            command=self.on_right_click_change,
            font=ctk.CTkFont(size=13)
        )
        right_click_switch.pack(anchor="w", pady=5)

        # Hide to tray
        self.hide_tray_var = ctk.BooleanVar(value=self.config["hide_on_minimize"])
        hide_tray_switch = ctk.CTkSwitch(
            options_inner,
            text="Minimizar para bandeja",
            variable=self.hide_tray_var,
            command=self.on_hide_tray_change,
            font=ctk.CTkFont(size=13)
        )
        hide_tray_switch.pack(anchor="w", pady=5)

        # ============= HOTKEY =============
        hotkey_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        hotkey_frame.pack(fill="x", pady=(0, 15))

        hotkey_inner = ctk.CTkFrame(hotkey_frame, fg_color="transparent")
        hotkey_inner.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            hotkey_inner,
            text="Atalho de Teclado",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        hotkey_input_frame = ctk.CTkFrame(hotkey_inner, fg_color="transparent")
        hotkey_input_frame.pack(fill="x")

        self.hotkey_entry = ctk.CTkEntry(
            hotkey_input_frame,
            placeholder_text="Ex: <ctrl>+<shift>+a",
            font=ctk.CTkFont(size=13)
        )
        self.hotkey_entry.insert(0, self.config["hotkey"])
        self.hotkey_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            hotkey_input_frame,
            text="Aplicar",
            width=80,
            command=self.on_hotkey_change,
            font=ctk.CTkFont(size=13)
        ).pack(side="right")

        # ============= INSTRUÇÕES =============
        instructions_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        instructions_frame.pack(fill="x")

        instructions_inner = ctk.CTkFrame(instructions_frame, fg_color="transparent")
        instructions_inner.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            instructions_inner,
            text="Como usar:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        instructions = [
            "1. Ative clicando no scroll ou usando o atalho",
            "2. SEGURE o botão do mouse = cliques automáticos",
            "3. SOLTE o botão = para de clicar imediatamente"
        ]

        for instruction in instructions:
            ctk.CTkLabel(
                instructions_inner,
                text=instruction,
                font=ctk.CTkFont(size=11),
                text_color="gray70"
            ).pack(anchor="w", pady=2)

    def on_cps_change(self, value):
        """Callback para mudança no slider de CPS"""
        cps = int(value)
        self.cps_value_label.configure(text=str(cps))
        self.config["cps"] = cps
        if self.clicker:
            self.clicker.set_cps(cps)
        self.save_config()

    def on_right_click_change(self):
        """Callback para mudança na opção de botão direito"""
        enabled = self.right_click_var.get()
        self.config["enable_right_click"] = enabled
        if self.clicker:
            self.clicker.set_right_click(enabled)
        self.save_config()

    def on_hide_tray_change(self):
        """Callback para mudança na opção de minimizar para bandeja"""
        self.config["hide_on_minimize"] = self.hide_tray_var.get()
        self.save_config()

        if self.config["hide_on_minimize"]:
            self.create_tray_icon()
        else:
            self.destroy_tray_icon()

    def on_hotkey_change(self):
        """Callback para mudança no atalho de teclado"""
        new_hotkey = self.hotkey_entry.get().strip()
        if new_hotkey:
            self.config["hotkey"] = new_hotkey
            if self.clicker:
                self.clicker.set_hotkey(new_hotkey)
            self.save_config()

            # Feedback visual
            original_color = self.hotkey_entry.cget("border_color")
            self.hotkey_entry.configure(border_color="green")
            self.window.after(1000, lambda: self.hotkey_entry.configure(border_color=original_color))

    def status_callback(self, enabled):
        """Callback chamado quando o status do auto-clicker muda"""
        self.is_enabled = enabled

        if enabled:
            self.status_indicator.configure(text_color="#22c55e")
            self.status_label.configure(text="Ativado")
            self.status_subtitle.configure(text="Segure o botão para clicar, solte para parar")
        else:
            self.status_indicator.configure(text_color="#ef4444")
            self.status_label.configure(text="Desativado")
            self.status_subtitle.configure(text="Use scroll ou atalho para ativar")

        # Atualiza ícone da bandeja se existir
        if self.tray_icon:
            self.update_tray_icon()

    def start_clicker(self):
        """Inicia o auto-clicker"""
        self.clicker = AutoClicker(
            cps=self.config["cps"],
            enable_right_click=self.config["enable_right_click"],
            hotkey=self.config["hotkey"],
            status_callback=self.status_callback
        )
        self.clicker.start()

    def create_tray_icon(self):
        """Cria o ícone na bandeja do sistema"""
        if self.tray_icon:
            return

        # Cria uma imagem simples para o ícone
        def create_icon_image(color="red"):
            width = 64
            height = 64
            image = Image.new('RGB', (width, height), color='black')
            dc = ImageDraw.Draw(image)
            dc.ellipse([16, 16, 48, 48], fill=color)
            return image

        icon_image = create_icon_image("red")

        menu = pystray.Menu(
            pystray.MenuItem("Mostrar", self.show_window),
            pystray.MenuItem("Sair", self.quit_app)
        )

        self.tray_icon = pystray.Icon("AutoClicker", icon_image, "AutoClicker Pro", menu)

        # Inicia a bandeja em uma thread separada
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def update_tray_icon(self):
        """Atualiza o ícone da bandeja do sistema"""
        if not self.tray_icon:
            return

        def create_icon_image(color="red"):
            width = 64
            height = 64
            image = Image.new('RGB', (width, height), color='black')
            dc = ImageDraw.Draw(image)
            dc.ellipse([16, 16, 48, 48], fill=color)
            return image

        color = "green" if self.is_enabled else "red"
        self.tray_icon.icon = create_icon_image(color)

    def destroy_tray_icon(self):
        """Destrói o ícone da bandeja"""
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def show_window(self, icon=None, item=None):
        """Mostra a janela"""
        self.window.deiconify()
        self.window.lift()
        self.hidden = False

    def hide_window(self):
        """Esconde a janela"""
        self.window.withdraw()
        self.hidden = True

    def on_closing(self):
        """Callback para fechamento da janela"""
        if self.config["hide_on_minimize"] and not self.hidden:
            self.hide_window()
        else:
            self.quit_app()

    def quit_app(self, icon=None, item=None):
        """Encerra o aplicativo"""
        if self.clicker:
            self.clicker.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.window.quit()
        sys.exit(0)

    def run(self):
        """Inicia a interface gráfica"""
        # Cria o ícone da bandeja se necessário
        if self.config["hide_on_minimize"]:
            self.create_tray_icon()

        self.window.mainloop()

if __name__ == "__main__":
    app = AutoClickerGUI()
    app.run()
