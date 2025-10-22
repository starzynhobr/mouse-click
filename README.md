# AutoClicker Pro

Um auto-clicker leve, moderno e de alto desempenho para Windows, construído com uma interface limpa em CustomTkinter e um hook de mouse de baixo nível (low-level) para detecção precisa.

Projetado para ser "Hold-to-Click": você ativa o modo e, em seguida, segura o botão do mouse para disparar os cliques. Solte para parar.

* **Interface Moderna:** Feita com CustomTkinter para um visual limpo e agradável.
* **Ajuste de CPS:** Slider para controlar os cliques por segundo (CPS) em tempo real.
* **Modo "Hold-to-Click":** Só clica automaticamente enquanto você **segura** o botão do mouse.
* **Detecção Precisa:** Usa um hook de baixo nível (`WH_MOUSE_LL`) para diferenciar cliques físicos de cliques injetados (programáticos), evitando loops infinitos.
* **Ativação Rápida:** Ative/Desative o auto-clicker com o **clique do scroll (botão do meio)** ou um **atalho de teclado** configurável.
* **Suporte ao Botão Direito:** Opção para habilitar o auto-click também no botão direito.
* **Minimizar para Bandeja:** Opção para esconder a janela na bandeja do sistema (ao lado do relógio).

## 🚀 Como Usar (Executável)

1.  Baixe o `gui.exe` na seção **Releases** deste repositório.
2.  Execute o `gui.exe` (recomenda-se executar como administrador para que o hook funcione em todos os programas).
3.  Use o **clique do scroll (botão do meio)** ou o atalho de teclado (padrão: `<ctrl>+<shift>+a`) para **ATIVAR** o modo.
4.  **SEGURE** o botão esquerdo (ou direito, se habilitado) para começar a clicar.
5.  **SOLTE** o botão para parar os cliques.

## 🛠️ Para Desenvolvedores (Rodando do Código)

Este projeto foi construído em Python 3.12.

1.  **Clone o repositório:**
    ```bash
    git clone [[https://github.com/SEU_USUARIO/SEU_REPO.git](https://github.com/SEU_USUARIO/SEU_REPO.git)](https://github.com/starzynhobr/mouse-click.git)
    ```

2.  **Crie e ative um ambiente virtual (venv):**
    ```bash
    # Recomendado: uv (é insanamente rápido)
    uv venv
    source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
    ```

3.  **Instale as dependências:**
    ```bash
    # As dependências são customtkinter, pystray, e pynput
    uv pip install customtkinter pystray pynput
    ```

4.  **Execute o programa:**
    ```bash
    python gui.py
    ```

## 📦 Compilando (Nuitka)

Para gerar o `.exe` único, use o Nuitka:

1.  **Instale o Nuitka:**
    ```bash
    uv pip install nuitka
    ```

2.  **Execute o comando de compilação (via PowerShell):**
    ```powershell
    python -m nuitka --onefile --windows-console-mode=disable --enable-plugin=tk-inter --include-package=customtkinter --include-data-file="config.json=config.json" --output-dir=dist gui.py
    ```

3.  O `gui.exe` estará na pasta `dist`.
