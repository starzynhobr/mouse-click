"""
Modern GUI for the auto-clicker using CustomTkinter.
"""

import json
import os
import sys
import threading

import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw

from auto_clicker import AutoClicker


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


TRANSLATIONS = {
    "pt": {
        "language_label": "PT",
        "title": "AutoClicker Pro",
        "subtitle": "Controle avançado de cliques automáticos",
        "status_on": "Ativado",
        "status_off": "Desativado",
        "status_inactive": "Use scroll ou {hotkey} para ativar",
        "status_active_hold": "Segure o botão para clicar, solte para parar",
        "status_active_burst": "Pressione para disparar {count} cliques em rajada",
        "cps_label": "Clicks por Segundo",
        "cps_hint": "Recomendado: 20 clicks/s",
        "options": "Opções",
        "right_click": "Habilitar botão direito",
        "hide_tray": "Minimizar para bandeja",
        "burst_mode": "Modo rajada ao pressionar",
        "burst_count": "Cliques por disparo",
        "burst_help": "Cada pressionamento dispara X cliques o mais rápido possível",
        "burst_speed_note": "O CPS acima afeta apenas o modo padrão de clique contínuo",
        "burst_warning": "Aviso: acima de 50 cliques pode causar sequências longas ou imprevisíveis no app alvo.",
        "hotkey_title": "Atalho de Teclado",
        "hotkey_placeholder": "Ex: <ctrl>+<shift>+a",
        "apply": "Aplicar",
        "instructions_title": "Como usar:",
        "instruction_1": "1. Ative clicando no scroll ou usando {hotkey}",
        "instruction_2": "2. Modo padrão: segure o botão para clicar continuamente",
        "instruction_3": "3. Modo rajada: um clique físico dispara a quantidade configurada em velocidade máxima",
        "tray_show": "Mostrar",
        "tray_exit": "Sair",
        "no_hotkey": "Atalho não definido",
    },
    "en": {
        "language_label": "EN",
        "title": "AutoClicker Pro",
        "subtitle": "Advanced control for automatic clicking",
        "status_on": "Enabled",
        "status_off": "Disabled",
        "status_inactive": "Use the scroll button or {hotkey} to enable",
        "status_active_hold": "Hold the button to click, release to stop",
        "status_active_burst": "Press to fire a burst of {count} clicks",
        "cps_label": "Clicks per Second",
        "cps_hint": "Recommended: 20 clicks/s",
        "options": "Options",
        "right_click": "Enable right button",
        "hide_tray": "Minimize to tray",
        "burst_mode": "Burst mode on press",
        "burst_count": "Clicks per burst",
        "burst_help": "Each press fires X clicks as fast as possible",
        "burst_speed_note": "The CPS above only affects the default continuous-click mode",
        "burst_warning": "Warning: values above 50 may create long or unpredictable click sequences in the target app.",
        "hotkey_title": "Keyboard Shortcut",
        "hotkey_placeholder": "Ex: <ctrl>+<shift>+a",
        "apply": "Apply",
        "instructions_title": "How to use:",
        "instruction_1": "1. Enable it with the scroll button or {hotkey}",
        "instruction_2": "2. Default mode: hold the button for continuous clicking",
        "instruction_3": "3. Burst mode: one physical click fires the configured amount at maximum speed",
        "tray_show": "Show",
        "tray_exit": "Exit",
        "no_hotkey": "No shortcut defined",
    },
}


class AutoClickerGUI:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("AutoClicker Pro")
        self.window.geometry("420x760")
        self.window.resizable(False, False)

        self.config_file = "config.json"
        self.config = self.load_config()

        self.clicker = None
        self.is_enabled = False
        self.hidden = False
        self.tray_icon = None
        self.instruction_labels = []

        self.create_widgets()
        self.start_clicker()
        self.refresh_ui_texts()

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        default_config = {
            "cps": 20,
            "enable_right_click": False,
            "hotkey": "<ctrl>+<shift>+a",
            "hide_on_minimize": False,
            "burst_mode": False,
            "burst_clicks": 3,
            "language": "pt",
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Erro ao carregar config: {e}")

        if default_config["language"] not in TRANSLATIONS:
            default_config["language"] = "pt"

        return default_config

    def save_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")

    def t(self, key, **kwargs):
        text = TRANSLATIONS[self.config["language"]][key]
        return text.format(**kwargs) if kwargs else text

    def format_hotkey_display(self, hotkey):
        replacements = {
            "<ctrl>": "Ctrl",
            "<shift>": "Shift",
            "<alt>": "Alt",
            "<cmd>": "Win",
            "<super>": "Win",
        }

        display_hotkey = hotkey
        for raw_value, display_value in replacements.items():
            display_hotkey = display_hotkey.replace(raw_value, display_value)

        parts = [part.strip() for part in display_hotkey.split("+") if part.strip()]
        formatted_parts = []
        for part in parts:
            if len(part) == 1 and part.isalpha():
                formatted_parts.append(part.upper())
            else:
                formatted_parts.append(part)

        return "+".join(formatted_parts) if formatted_parts else self.t("no_hotkey")

    def get_inactive_status_text(self):
        return self.t("status_inactive", hotkey=self.format_hotkey_display(self.config["hotkey"]))

    def get_active_status_text(self):
        if self.config["burst_mode"]:
            return self.t("status_active_burst", count=self.config["burst_clicks"])
        return self.t("status_active_hold")

    def get_instruction_texts(self):
        hotkey = self.format_hotkey_display(self.config["hotkey"])
        return [
            self.t("instruction_1", hotkey=hotkey),
            self.t("instruction_2"),
            self.t("instruction_3"),
        ]

    def update_burst_warning(self):
        if self.config["burst_clicks"] > 50:
            self.burst_warning_label.configure(text=self.t("burst_warning"))
        else:
            self.burst_warning_label.configure(text="")

    def refresh_ui_texts(self):
        self.lang_var.set(self.config["language"].upper())
        self.title_label.configure(text=self.t("title"))
        self.subtitle_label.configure(text=self.t("subtitle"))
        self.status_label.configure(text=self.t("status_on") if self.is_enabled else self.t("status_off"))
        self.status_subtitle.configure(
            text=self.get_active_status_text() if self.is_enabled else self.get_inactive_status_text()
        )
        self.cps_title_label.configure(text=self.t("cps_label"))
        self.cps_hint_label.configure(text=self.t("cps_hint"))
        self.options_title_label.configure(text=self.t("options"))
        self.right_click_switch.configure(text=self.t("right_click"))
        self.hide_tray_switch.configure(text=self.t("hide_tray"))
        self.burst_mode_switch.configure(text=self.t("burst_mode"))
        self.burst_count_label.configure(text=self.t("burst_count"))
        self.burst_help_label.configure(text=self.t("burst_help"))
        self.burst_speed_label.configure(text=self.t("burst_speed_note"))
        self.hotkey_title_label.configure(text=self.t("hotkey_title"))
        self.hotkey_entry.configure(placeholder_text=self.t("hotkey_placeholder"))
        self.apply_hotkey_button.configure(text=self.t("apply"))
        self.instructions_title_label.configure(text=self.t("instructions_title"))

        for label, text in zip(self.instruction_labels, self.get_instruction_texts()):
            label.configure(text=text)

        self.update_burst_warning()

        if self.tray_icon:
            self.destroy_tray_icon()
            if self.config["hide_on_minimize"] or self.hidden:
                self.create_tray_icon()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=18)

        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 18))

        top_bar = ctk.CTkFrame(header_frame, fg_color="transparent")
        top_bar.pack(fill="x")

        self.lang_var = ctk.StringVar(value=self.config["language"].upper())
        self.language_selector = ctk.CTkSegmentedButton(
            top_bar,
            values=["PT", "EN"],
            variable=self.lang_var,
            command=self.on_language_change,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28
        )
        self.language_selector.pack(side="right")

        self.title_label = ctk.CTkLabel(
            header_frame,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.title_label.pack(pady=(10, 0))

        self.subtitle_label = ctk.CTkLabel(
            header_frame,
            font=ctk.CTkFont(size=12),
            text_color="gray60",
            wraplength=330,
            justify="center",
        )
        self.subtitle_label.pack(pady=(6, 0))

        status_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        status_frame.pack(fill="x", pady=(0, 18))

        status_inner = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_inner.pack(fill="x", padx=20, pady=16)

        self.status_indicator = ctk.CTkLabel(
            status_inner,
            text="●",
            font=ctk.CTkFont(size=38),
            text_color="#ef4444",
        )
        self.status_indicator.pack(side="left", padx=(0, 16))

        status_text_frame = ctk.CTkFrame(status_inner, fg_color="transparent")
        status_text_frame.pack(side="left", fill="x", expand=True)

        self.status_label = ctk.CTkLabel(
            status_text_frame,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.status_label.pack(anchor="w")

        self.status_subtitle = ctk.CTkLabel(
            status_text_frame,
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            wraplength=250,
            justify="left",
        )
        self.status_subtitle.pack(anchor="w", pady=(2, 0))

        cps_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        cps_frame.pack(fill="x", pady=(0, 15))

        cps_inner = ctk.CTkFrame(cps_frame, fg_color="transparent")
        cps_inner.pack(fill="x", padx=20, pady=15)

        cps_header = ctk.CTkFrame(cps_inner, fg_color="transparent")
        cps_header.pack(fill="x", pady=(0, 10))

        self.cps_title_label = ctk.CTkLabel(
            cps_header,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.cps_title_label.pack(side="left")

        self.cps_value_label = ctk.CTkLabel(
            cps_header,
            text=str(self.config["cps"]),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3b82f6",
        )
        self.cps_value_label.pack(side="right")

        self.cps_slider = ctk.CTkSlider(
            cps_inner,
            from_=1,
            to=50,
            number_of_steps=49,
            command=self.on_cps_change,
        )
        self.cps_slider.set(self.config["cps"])
        self.cps_slider.pack(fill="x", pady=(0, 6))

        self.cps_hint_label = ctk.CTkLabel(
            cps_inner,
            font=ctk.CTkFont(size=10),
            text_color="gray60",
        )
        self.cps_hint_label.pack(anchor="center")

        options_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        options_frame.pack(fill="x", pady=(0, 15))

        options_inner = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_inner.pack(fill="x", padx=20, pady=15)

        self.options_title_label = ctk.CTkLabel(
            options_inner,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.options_title_label.pack(anchor="w", pady=(0, 10))

        self.right_click_var = ctk.BooleanVar(value=self.config["enable_right_click"])
        self.right_click_switch = ctk.CTkSwitch(
            options_inner,
            variable=self.right_click_var,
            command=self.on_right_click_change,
            font=ctk.CTkFont(size=13),
        )
        self.right_click_switch.pack(anchor="w", pady=5)

        self.hide_tray_var = ctk.BooleanVar(value=self.config["hide_on_minimize"])
        self.hide_tray_switch = ctk.CTkSwitch(
            options_inner,
            variable=self.hide_tray_var,
            command=self.on_hide_tray_change,
            font=ctk.CTkFont(size=13),
        )
        self.hide_tray_switch.pack(anchor="w", pady=5)

        self.burst_mode_var = ctk.BooleanVar(value=self.config["burst_mode"])
        self.burst_mode_switch = ctk.CTkSwitch(
            options_inner,
            variable=self.burst_mode_var,
            command=self.on_burst_mode_change,
            font=ctk.CTkFont(size=13),
        )
        self.burst_mode_switch.pack(anchor="w", pady=5)

        burst_count_frame = ctk.CTkFrame(options_inner, fg_color="transparent")
        burst_count_frame.pack(fill="x", pady=(10, 0))

        self.burst_count_label = ctk.CTkLabel(
            burst_count_frame,
            font=ctk.CTkFont(size=13),
        )
        self.burst_count_label.pack(side="left")

        self.burst_clicks_value_label = ctk.CTkLabel(
            burst_count_frame,
            text=str(self.config["burst_clicks"]),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#3b82f6",
        )
        self.burst_clicks_value_label.pack(side="right")

        self.burst_clicks_slider = ctk.CTkSlider(
            options_inner,
            from_=1,
            to=500,
            number_of_steps=499,
            command=self.on_burst_clicks_change,
        )
        self.burst_clicks_slider.set(self.config["burst_clicks"])
        self.burst_clicks_slider.pack(fill="x", pady=(8, 0))

        self.burst_help_label = ctk.CTkLabel(
            options_inner,
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            wraplength=320,
            justify="left",
        )
        self.burst_help_label.pack(anchor="w", pady=(6, 0))

        self.burst_speed_label = ctk.CTkLabel(
            options_inner,
            font=ctk.CTkFont(size=10),
            text_color="gray60",
            wraplength=320,
            justify="left",
        )
        self.burst_speed_label.pack(anchor="w", pady=(3, 0))

        self.burst_warning_label = ctk.CTkLabel(
            options_inner,
            text="",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#f59e0b",
            wraplength=320,
            justify="left",
        )
        self.burst_warning_label.pack(anchor="w", pady=(5, 0))

        hotkey_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        hotkey_frame.pack(fill="x", pady=(0, 15))

        hotkey_inner = ctk.CTkFrame(hotkey_frame, fg_color="transparent")
        hotkey_inner.pack(fill="x", padx=20, pady=15)

        self.hotkey_title_label = ctk.CTkLabel(
            hotkey_inner,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.hotkey_title_label.pack(anchor="w", pady=(0, 10))

        hotkey_input_frame = ctk.CTkFrame(hotkey_inner, fg_color="transparent")
        hotkey_input_frame.pack(fill="x")

        self.hotkey_entry = ctk.CTkEntry(
            hotkey_input_frame,
            font=ctk.CTkFont(size=13),
        )
        self.hotkey_entry.insert(0, self.config["hotkey"])
        self.hotkey_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.apply_hotkey_button = ctk.CTkButton(
            hotkey_input_frame,
            width=84,
            command=self.on_hotkey_change,
            font=ctk.CTkFont(size=13),
        )
        self.apply_hotkey_button.pack(side="right")

        instructions_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color="#1a1a1a")
        instructions_frame.pack(fill="x")

        instructions_inner = ctk.CTkFrame(instructions_frame, fg_color="transparent")
        instructions_inner.pack(fill="x", padx=20, pady=15)

        self.instructions_title_label = ctk.CTkLabel(
            instructions_inner,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.instructions_title_label.pack(anchor="w", pady=(0, 6))

        for _ in range(3):
            label = ctk.CTkLabel(
                instructions_inner,
                font=ctk.CTkFont(size=11),
                text_color="gray70",
                wraplength=320,
                justify="left",
            )
            label.pack(anchor="w", pady=2)
            self.instruction_labels.append(label)

    def on_language_change(self, value):
        self.config["language"] = value.lower()
        self.save_config()
        self.refresh_ui_texts()

    def on_cps_change(self, value):
        cps = int(value)
        self.cps_value_label.configure(text=str(cps))
        self.config["cps"] = cps
        if self.clicker:
            self.clicker.set_cps(cps)
        self.save_config()

    def on_right_click_change(self):
        enabled = self.right_click_var.get()
        self.config["enable_right_click"] = enabled
        if self.clicker:
            self.clicker.set_right_click(enabled)
        self.save_config()

    def on_hide_tray_change(self):
        self.config["hide_on_minimize"] = self.hide_tray_var.get()
        self.save_config()

        if self.config["hide_on_minimize"]:
            self.create_tray_icon()
        else:
            self.destroy_tray_icon()

    def on_burst_mode_change(self):
        enabled = self.burst_mode_var.get()
        self.config["burst_mode"] = enabled
        if self.clicker:
            self.clicker.set_burst_mode(enabled)
        self.save_config()
        if self.is_enabled:
            self.status_subtitle.configure(text=self.get_active_status_text())

    def on_burst_clicks_change(self, value):
        clicks = int(value)
        self.burst_clicks_value_label.configure(text=str(clicks))
        self.config["burst_clicks"] = clicks
        if self.clicker:
            self.clicker.set_burst_clicks(clicks)
        self.save_config()
        self.update_burst_warning()
        if self.is_enabled and self.config["burst_mode"]:
            self.status_subtitle.configure(text=self.get_active_status_text())

    def on_hotkey_change(self):
        new_hotkey = self.hotkey_entry.get().strip()
        if new_hotkey:
            self.config["hotkey"] = new_hotkey
            if self.clicker:
                self.clicker.set_hotkey(new_hotkey)
            self.save_config()
            self.refresh_ui_texts()

            original_color = self.hotkey_entry.cget("border_color")
            self.hotkey_entry.configure(border_color="green")
            self.window.after(1000, lambda: self.hotkey_entry.configure(border_color=original_color))

    def status_callback(self, enabled):
        self.is_enabled = enabled

        if enabled:
            self.status_indicator.configure(text_color="#22c55e")
            self.status_label.configure(text=self.t("status_on"))
            self.status_subtitle.configure(text=self.get_active_status_text())
        else:
            self.status_indicator.configure(text_color="#ef4444")
            self.status_label.configure(text=self.t("status_off"))
            self.status_subtitle.configure(text=self.get_inactive_status_text())

        if self.tray_icon:
            self.update_tray_icon()

    def start_clicker(self):
        self.clicker = AutoClicker(
            cps=self.config["cps"],
            enable_right_click=self.config["enable_right_click"],
            hotkey=self.config["hotkey"],
            burst_mode=self.config["burst_mode"],
            burst_clicks=self.config["burst_clicks"],
            status_callback=self.status_callback,
        )
        self.clicker.start()

    def create_tray_icon(self):
        if self.tray_icon:
            return

        def create_icon_image(color="red"):
            width = 64
            height = 64
            image = Image.new("RGB", (width, height), color="black")
            dc = ImageDraw.Draw(image)
            dc.ellipse([16, 16, 48, 48], fill=color)
            return image

        icon_image = create_icon_image("red")

        menu = pystray.Menu(
            pystray.MenuItem(self.t("tray_show"), self.show_window),
            pystray.MenuItem(self.t("tray_exit"), self.quit_app),
        )

        self.tray_icon = pystray.Icon("AutoClicker", icon_image, self.t("title"), menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def update_tray_icon(self):
        if not self.tray_icon:
            return

        def create_icon_image(color="red"):
            width = 64
            height = 64
            image = Image.new("RGB", (width, height), color="black")
            dc = ImageDraw.Draw(image)
            dc.ellipse([16, 16, 48, 48], fill=color)
            return image

        color = "green" if self.is_enabled else "red"
        self.tray_icon.icon = create_icon_image(color)
        self.tray_icon.title = self.t("title")

    def destroy_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def show_window(self, icon=None, item=None):
        self.window.deiconify()
        self.window.lift()
        self.hidden = False

    def hide_window(self):
        self.window.withdraw()
        self.hidden = True

    def on_closing(self):
        if self.config["hide_on_minimize"] and not self.hidden:
            self.hide_window()
        else:
            self.quit_app()

    def quit_app(self, icon=None, item=None):
        if self.clicker:
            self.clicker.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.window.quit()
        sys.exit(0)

    def run(self):
        if self.config["hide_on_minimize"]:
            self.create_tray_icon()

        self.window.mainloop()


if __name__ == "__main__":
    app = AutoClickerGUI()
    app.run()
